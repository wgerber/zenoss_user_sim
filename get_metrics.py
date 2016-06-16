import argparse
import datetime
import json
import logging
import os
import pytz
import requests
import sys
import time

import pandas as pd
from pandas import DataFrame, Series
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.getLogger("requests").setLevel(logging.WARNING)


def set_up_logger():
    log_format = "" # %(asctime)s [%(name)s] %(levelname)s %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

set_up_logger()

log = logging.getLogger("metric_analyzer")


class BCOLORS:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


class MetricRetriever(object):
    """ Class to retrieve the zrequest_duration metric from opentsdb """

    BASE_METRIC_URL = "{0}/api/query?start={1}&end={2}&m=max:{3}{4}"

    def __init__(self, opentsdb_url):
        self.opentsdb_url = opentsdb_url.rstrip("/ ")

    def _query(self, query_url):
        data = []
        resp=requests.get(query_url, verify=False, stream=True)
        if resp.ok:
            data = json.loads(resp.content)
            resp.close()
        else:
            log.error("Error retrieving data: {0}"
                    .format(resp.json()['error']['message']))
        return data

    def _parse_raw_datum(self, raw_datum):
        datapoints = []
        for ts, value in raw_datum.get("dps", {}).iteritems():
            datapoint = {}
            datapoint["metric"] = raw_datum["metric"]
            datapoint["ts"] = float(ts)
            datapoint["value"] = value
            tags = raw_datum.get("tags")
            if tags:
                for tag, tag_value in tags.iteritems():
                    datapoint[tag] = tag_value
            datapoints.append(datapoint)
        return datapoints

    def get_datapoints(self, start, end, metric, tags):
        """ start and end are timestamps and should be in UTC """
        tag_text = "{" + ",".join([ "{0}=*".format(tag) for tag in tags ]) + "}"
        query_url = self.BASE_METRIC_URL.format(self.opentsdb_url, start, end, metric, tag_text)
        data = self._query(query_url)
        datapoints = []
        for datum in data:
            datapoints.extend(self._parse_raw_datum(datum))
        return datapoints


class MetricAnalyzer(object):

    def __init__(self, metric_name, datapoints):
        self.metric_name = metric_name
        self.datapoints = datapoints
        self.df = DataFrame(datapoints)
        self.df["start"] = self.df["ts"] - self.df["value"]*1000

    def get_summary(self):
        summary = {}
        summary["min"] = self.df['value'].min()
        summary["max"] = self.df['value'].max()
        summary["mean"] = self.df['value'].mean()
        summary["count"] = self.df['value'].count()
        summary['std'] = self.df['value'].std()
        return summary

    def print_metric_summary(self):
        summary = self.get_summary()
        format_text = ("Metric {0} => "
                       "count: {1}  |  min: {2}  |  max:{3}  |  mean:{4}  |  "
                       "std:{5}")
        count_text = "{0}".format(summary.get("count")).rjust(10)
        min_text = "{0:0.4f}".format(summary.get("min")).rjust(10)
        max_text = "{0:0.4f}".format(summary.get("max")).rjust(10)
        mean_text = "{0:0.4f}".format(summary.get("mean")).rjust(10)
        stdev_text = "{0:0.4f}".format(summary.get("std")).rjust(10)
        log.info(format_text.format(
            self.metric_name.rjust(20), count_text, min_text, max_text,
            mean_text, stdev_text))

    def get_top_n_by(self, by_col, cols, n=25, df=None):
        if df is None:
            df = self.df
        return df[ cols ].sort_values(by_col,  ascending=False)[0:n]

    def print_top_n_by(self, by_col, cols, n=25, df=None):
        log.info("{0}--  Top {1} calls sorted by {2}  --  {3}".format(BCOLORS.YELLOW, n, by_col, BCOLORS.ENDC))
        top_n_df = self.get_top_n_by(by_col, cols, n, df)
        for val in top_n_df.values:
            log.info("{0}: {1} => {2}".format(*val))

class RequestDurationMetricAnalyzer(MetricAnalyzer):

    def __init__(self, metric_name, datapoints):
        super(RequestDurationMetricAnalyzer, self).__init__(metric_name, datapoints)

    def get_calls_by_action(self, df):
        by_action = df.sort_values(by='value', ascending=False).groupby('action')
        actions = []
        for action, metrics_df in by_action:
            action_data = {}
            action_data['action'] = action
            action_data['mean'] = metrics_df['value'].mean()
            action_data['count'] = metrics_df['value'].count()
            action_data['max'] = metrics_df['value'].max()
            action_data['min'] = metrics_df['value'].min()
            actions.append(action_data)
        return actions

    def get_calls_by_zopes_and_action(self, df):
        by_zope = {}
        for zope_id in df['zope'].unique():
            by_action = self.get_calls_by_action(df[df['zope']==zope_id])
            by_zope[zope_id] = by_action
        return by_zope


    def print_by_action_data(self, by_action):
        for action_data in by_action:
            log.info("Action: {0}".format(action_data.get("action")))
            log.info("\tcount: {0}, min: {1:0.4f}, max:{2:0.4f}, mean:{3:0.4f}".format(action_data.get("count"), action_data.get("min"), action_data.get("max"), action_data.get("mean")))

    def print_getInfo_calls(self, df):
        getInfo_df = df[df["action"]=="-DeviceRouter-getInfo-"][["start", "path", "value"]].sort_values(by='start')
        for val in getInfo_df.values:
            log.info("{0}: {1} => {2}".format(val[0], val[1], val[2]))

    def print_calls_by_start(self, df):
        by_start_df = df[["start", "path", "value"]].sort_values(by='start')
        for val in by_start_df.values:
            log.info("{0}: {1} => {2}".format(val[0], val[1], val[2]))

    def print_top_n_by_duration(self, df, n=20):
        top_n_df = df[["action", "path", "value"]].sort_values(by='value',  ascending=False)[0:n]
        for val in top_n_df.values:
            log.info("{0}: {1} => {2}".format(val[0], val[1], val[2]))


class WaitTimeMetricAnalyzer(MetricAnalyzer):

    def __init__(self, metric_name, datapoints):
        super(WaitTimeMetricAnalyzer, self).__init__(metric_name, datapoints)

    def print_by_action(self):
        grouped = self.df.groupby('action')['value']
        log.info('')
        log.info('{:^75}'.format('Group by Actions'))
        log.info('{:^31}{:^10}{:^10}{:^10}{:^10}{:^10}'
                .format('action', 'count', 'min', 'max', 'mean', 'std'))
        for action, group in grouped:
            summary = get_summary(group)
            action_text = '{:>31}'.format(action)
            count_text = "{0}".format(summary.get("count")).rjust(10)
            min_text = "{0:0.2f}".format(summary.get("min")).rjust(10)
            max_text = "{0:0.2f}".format(summary.get("max")).rjust(10)
            mean_text = "{0:0.2f}".format(summary.get("mean")).rjust(10)
            std_text = "{0:0.2f}".format(summary.get("std")).rjust(10)
            log.info('{}{}{}{}{}{}'
                    .format(action_text, count_text, min_text, max_text,
                            mean_text, std_text))
        log.info('')

class WorkflowMetricAnalyzer(MetricAnalyzer):

    def __init__(self, metric_name, datapoints):
        super(WorkflowMetricAnalyzer, self).__init__(metric_name, datapoints)

    def print_by_workflow(self):
        grouped = self.df.groupby('workflow')['value']
        sum_completed = 0
        sum_failed = 0
        log.info('')
        log.info('{:^75}'.format('Group by Workflows'))
        log.info('{:^25}{:^10}{:^10}'
                .format('workflow', 'completed', 'failed'))
        for workflow, group in grouped:
            workflow_text = '{:>25}'.format(workflow)
            try:
                completed =  group.value_counts()[1]
            except KeyError:
                completed = 0
            completed_text = "{}".format(completed).rjust(10)
            sum_completed += completed
            try:
                failed = group.value_counts()[0]
            except KeyError:
                failed = 0
            failed_text = "{}".format(failed).rjust(10)
            sum_failed += failed

            log.info('{}{}{}'
                    .format(workflow_text, completed_text, failed_text))
        log.info('{:>25}{:>10}{:>10}'.format('-'*len('total'), '-'*5, '-'*5))
        log.info('{:>25}{:>10}{:>10}'.format('total', sum_completed, sum_failed))
        log.info('')

def get_summary(series):
    summary = {}
    summary['count'] = series.count()
    summary['min'] = series.min()
    summary['max'] = series.max()
    summary['mean'] = series.mean()
    summary['std'] = series.std()
    return summary

def _datetime_to_epoch(date_):
    date_format = '%Y/%m/%d-%H:%M:%S'
    utc = pytz.timezone("UTC")
    dt=datetime.datetime.fromtimestamp(time.mktime(time.strptime(date_, date_format)))
    aware_dt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, tzinfo=pytz.UTC)
    return int((aware_dt - datetime.datetime(1970,1,1,tzinfo=pytz.UTC)).total_seconds())

def print_header(metric_name):
    log.info("{0}{1}{2}".format(BCOLORS.YELLOW, "-"*100, BCOLORS.ENDC))
    log.info("{0}ANALYSIS FOR {1}{2}".format(BCOLORS.YELLOW, metric_name, BCOLORS.ENDC).center(100))
    log.info("{0}{1}{2}".format(BCOLORS.YELLOW, "-"*100, BCOLORS.ENDC))

'''
def parse_options():
    """Defines command-line options for script """
    parser = argparse.ArgumentParser(version="1.0", description="Hack to remove objects from object_state")
    parser.add_argument("-d", "--detailed", dest="detailed", action="store_true", default=False, help="Do detailed metric analysis.")
    return vars(parser.parse_args())
'''

def countUser(tsdbUrl, startTime, endTime, simId):
    headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
    url = (tsdbUrl + "/api/query"
           + '?start=' + startTime
           + '&end=' + endTime
           + '&m=zimsum:1s-sum:userCountDelta')
    r = requests.get(
            url, data=json.dumps({}), headers=headers, verify=False)
    if not r.ok:
        print 'Failed to get user count deltas from tsdb'
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
            r = requests.post(
                    tsdbUrl + "/api/put",
                    data=json.dumps(part),
                    headers=headers, verify=False)

            if not r.ok:
                print 'Failed to post user count to tsdb'
                print r.json()['error']['message']

def get_stats(base_opentsdb_url, start, end, detailed):
    start = _datetime_to_epoch(start)
    end = _datetime_to_epoch(end)
    assert start<end

    log.debug("start: {0}  ||  end: {1}".format(start, end))

    metric_retiever = MetricRetriever(base_opentsdb_url)

    """ ANALYSIS FOR ZREQUEST.DURATION """
    print_header("ZREQUEST.DURATION")
    request_duration_datapoints = metric_retiever.get_datapoints(start, end, "zrequest.duration", ["zope", "user", "path", "action"])
    if request_duration_datapoints:
        request_duration_analyzer = RequestDurationMetricAnalyzer("zrequest.duration", request_duration_datapoints)
        request_duration_analyzer.print_metric_summary()
        if detailed:
            request_duration_analyzer.print_top_n_by("value", ["action", "path", "value"], n=1000)


    """ ANALYSIS FOR WAIT TIME """
    wait_time_datapoints = metric_retiever.get_datapoints(start, end, "waitTime", ["action", "user", "workflow"])
    if wait_time_datapoints:
        print_header("WAIT TIME")
        wait_time_analyzer = WaitTimeMetricAnalyzer("waitTime", wait_time_datapoints)
        wait_time_analyzer.print_metric_summary()
        wait_time_analyzer.print_by_action()
        if detailed:
            wait_time_analyzer.print_top_n_by("value", ["action", "user", "value"], n=50)

    # WORKFLOW
    workflow_datapoints = metric_retiever.get_datapoints(
            start, end, 'workflow', ['workflow', 'user', 'host'])
    if workflow_datapoints:
        print_header('WORKFLOW')
        workflow_analyzer = WorkflowMetricAnalyzer("workflow", workflow_datapoints)
        workflow_analyzer.print_by_workflow()

def main(base_opentsdb_url, start, end, simId, detailed):
    countUser(base_opentsdb_url, start, end, simId)
    get_stats(base_opentsdb_url, start, end, detailed)

def parse_args():
    parser = argparse.ArgumentParser(description="Post-process a simulation result")
    parser.add_argument("-u", "--url",
            help="full url of OpenTSDB, e.g., https://opentsdb.graveyard")
    parser.add_argument("-s", "--startTime",
            help="Simulation start time in UTC, e.g., 2016/06/01-13:00:00")
    parser.add_argument("-e", "--endTime",
            help="Simulation end time in UTC, e.g., 2016/06/01-13:00:00")
    parser.add_argument("-i", "--simId", default = '',
            help="Simulation ID for tagging")
    parser.add_argument("-d", "--detail", default = False,
            help="Print output in detail")

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

# python get_metrics.py 1464285106 1464285259

if __name__=="__main__":
    args = parse_args()
    main(args.url, args.startTime, args.endTime, args.simId, args.detail)
