import sys, random
import time, traceback, argparse
from xvfbwrapper import Xvfb
import multiprocessing as mp
import Queue

from workflows import MonitorEvents, LogInOutWorkflow, MonitorDashboard, InvestigateDevice
from user import *

def parse_args():
    parser = argparse.ArgumentParser(description="Spin up some simulated users")
    parser.add_argument("-u", "--url",
            help="full url of zenoss UI")
    parser.add_argument("-n", "--username",
            help="zenoss account username")
    parser.add_argument("-p", "--password",
            help="zenoss account password")
    parser.add_argument("--chromedriver-path", dest="chromedriver",
            default=None, help="path to chromedriver")
    parser.add_argument("-c", "--users",
            default=1, help="number of simulated users to create", type=int)
    parser.add_argument("--log-dir", dest="logDir",
            default="/tmp/", help="directory to store logs")
    parser.add_argument("--headless",
            dest="headless", action="store_true", help="if simulations should run headless")
    parser.add_argument("--no-headless",
            dest="headless", action="store_false", help="if simulations should run headless")
    parser.set_defaults(headless=True)
    parser.add_argument('--hour', dest = 'workHour', default = 0,
            help = 'duration in hours that workflows will be repeated', type = float)
    parser.add_argument('--workflows', dest = 'workflows', default = '',
            help = 'workflows to run, a comma separated string')
    parser.add_argument('--tsdb-url', dest = 'tsdbUrl', default = '',
            help = 'OpenTSDB URL')

    # TODO - skill level
    # TODO - workflow
    # TODO - more sensible defaults and argument config

    args = parser.parse_args()

    # TODO - pretty sure argparse can do this by default
    # and also better
    if not args.url:
        raise Exception("url is required")
    if not args.username:
        raise Exception("username is required")
    if not args.password:
        raise Exception("password is required")
    if not args.workflows:
        raise Exception('workflows are required')
    else:
        return args

def startUser(name, url, username, password, headless, logDir, chromedriver,
        workHour, workflowNames, tsdbQueue):
    if headless:
        xvfb = Xvfb(width=1100, height=800)
        xvfb.start()

    user = User(name, url=url, username=username, password=password,
            logDir=logDir, chromedriver=chromedriver, workHour=workHour,
            tsdbQueue=tsdbQueue)

    # TODO - configure workflow
    # Always start with Login() and end with Logout(). There has to be at least
    # one workflow between Login() and Logout().
    workflows = []
    workflows.append(LogInOutWorkflow.Login())

    workflowNames = [name.strip() for name in workflowNames.split(',')]
    for name in workflowNames:
        try:
            workflowClass = getattr(sys.modules[__name__], name)
        except AttributeError:
            user.log('Could not find workflow {}'.format(name), severity="ERROR")
            user.quit()

        workflows.append(workflowClass())

    workflows.append(LogInOutWorkflow.Logout())

    user.addWorkflow(workflows)

    try:
        user.work()
    except:
        user.log("%s raised an uncaught exception" % user.name, severity="ERROR")
        traceback.print_exc()
    finally:
        #log results
        resultsStr = ""
        for result in user.results:
            resultsStr += str(result)
            resultsStr += ","
        user.log(resultsStr, toConsole=False)
        print "cleaning up %s" % user.name
        user.quit()
        if headless:
            xvfb.stop()
        print "cleaned up %s" % user.name

def pushToTsdb(url, queue):
    data = []
    obj = None
    while obj != 'STOP':
        try:
            obj = queue.get(timeout=10)
            data += obj
        except Queue.Empty:
            headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
            if data:
                r=requests.post(url + "/api/put", data=json.dumps(data), headers=headers, verify=False)
            data = []

if __name__ == '__main__':
    try:
        args = parse_args()

        # create a folder for this run
        args.logDir = "%s/%s" % (args.logDir, time.time())
        if not os.path.exists(args.logDir):
            os.makedirs(args.logDir)

        # TODO - log additional args
        print ("starting %i users with options:\n"
            "    url: %s\n"
            "    username: %s\n"
            "    headless: %s\n"
            "    workflows: %s\n"
            "    logDir: %s") % (
                args.users, args.url, args.username, "True" if args.headless else "False", args.workflows, args.logDir)

        startTime = time.gmtime()

        tsdbQueue = mp.Queue()
        tsdbPusher = mp.Process(
                target = pushToTsdb, args = (args.tsdbUrl, tsdbQueue,))
        tsdbPusher.start()

        processes = []
        for i in xrange(args.users):
            # TODO - skill level
            # TODO - workflows
            p = mp.Process(target=startUser, args=(
                "bob%i"%i, args.url, args.username, args.password, args.headless, args.logDir, args.chromedriver, args.workHour, args.workflows, tsdbQueue))
            processes.append(p)
            p.start()
            # give xvfb time to grab a display before kicking off
            # a new request
            # prevent all users from logging in at once
            time.sleep(random.uniform(1,10))
        done = 0
        while done < args.users:
            toRemove = []
            for p in processes:
                if not p.is_alive():
                    toRemove.append(p)
                    done += 1
                    print colorizeString("%i down, %i to go" % (done, args.users - done), "DEBUG")
            for p in toRemove:
                processes.remove(p)

        tsdbQueue.put('STOP')
        tsdbQueue.close()
        tsdbQueue.join_thread()
    finally:
        endTime = time.gmtime()
        print colorizeString("all processes have exited", "DEBUG")
        print colorizeString("start: %s, end: %s" % \
                (time.strftime('%Y-%m-%dT%H:%M:%SZ', startTime),
                    time.strftime('%Y-%m-%dT%H:%M:%SZ', endTime)), "DEBUG")
