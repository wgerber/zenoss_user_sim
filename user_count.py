import time, requests, json, argparse

from common import *

# disable warnings when posting to our tsdb
# with self-signed cert
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def parse_args():
    parser = argparse.ArgumentParser(description="Count users in a simuation")
    parser.add_argument("-u", "--url",
            help="full url of OpenTSDB")
    parser.add_argument("-s", "--startTime",
            help="Simulation start time in local time zone , e.g., 2016/06/01-13:00:00")
    parser.add_argument("-e", "--endTime",
            help="Simulation end time in local time zone, e.g., 2016/06/01-13:00:00")
    parser.add_argument("-i", "--simId",
            help="Simulation ID for tagging")

    args = parser.parse_args()

    # TODO - pretty sure argparse can do this by default
    # and also better
    if not args.url:
        raise Exception("url is required")
    if not args.startTime:
        raise Exception("start time is required")
    if not args.endTime:
        raise Exception("end time is required")
    if not args.simId:
        raise Exception('simulation id is required')
    else:
        return args

def countUser(tsdbUrl, startTime, endTime, simId):
    headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
    url = (tsdbUrl + "/api/query"
           + '?start=' + startTime
           + '&end=' + endTime
           + '&m=zimsum:1s-sum:userCountDelta')
    r = requests.get(
            url, data=json.dumps({}), headers=headers, verify=False)
    if not r.ok:
        print colorizeString('Failed to get user count deltas from tsdb', 'ERROR')
        print r.json()['error']['message']

    try:
        userCountDelta = r.json()[0]['dps']
    except IndexError:
        userCountDelta = []

    if userCountDelta:
        sortedTime = sorted(userCountDelta.keys())
        count = 0
        data = []
        for t in sortedTime:
            count += userCountDelta[t]
            data += [{'timestamp': int(t), 'metric': 'userCount', 'value': count, 'tags':{'simId': simId}}]

        bufferSize = 30 # messages
        for i in range(len(data)/bufferSize + 1):
            part = data[bufferSize*i:bufferSize*(i+1)]
            print part
            r = requests.post(
                    tsdbUrl + "/api/put",
                    data=json.dumps(part),
                    headers=headers, verify=False)

            if not r.ok:
                print colorizeString('Failed to post user count to tsdb', 'ERROR')
                print r.json()['error']['message']

if __name__ == '__main__':
    args = parse_args()

    countUser(args.url, args.startTime, args.endTime, args.simId)
