import sys, random
import time, traceback, argparse
from xvfbwrapper import Xvfb
import multiprocessing as mp
import Queue

from workflows import MonitorEvents, LogInOutWorkflow, MonitorDashboard, InvestigateDevice
from user import *

HOUR_TO_SEC = 3600

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
    parser.add_argument('--duration', dest = 'duration', default = 0,
            help = 'duration in seconds that workflows will be repeated', type = float)
    parser.add_argument('--workflows', dest = 'workflows', default = '',
            help = 'workflows to run, a comma separated string')
    parser.add_argument('--tsdb-url', dest = 'tsdbUrl', default = '',
            help = 'OpenTSDB URL')

    # TODO - skill level
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
        duration, workflowNames, tsdbQueue):
    if headless:
        xvfb = Xvfb(width=1100, height=800)
        xvfb.start()

    user = User(name, url=url, username=username, password=password,
            logDir=logDir, chromedriver=chromedriver, duration=duration,
            tsdbQueue=tsdbQueue)

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
            # When the timeout is too long, some data get lost.
            obj = queue.get(timeout=7)
            data += obj
        except Queue.Empty:
            headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
            if data:
                print 'Posting {} data points to tsdb'.format(len(data))
                r=requests.post(
                        url + "/api/put",
                        data=json.dumps(data), headers=headers, verify=False)
                print 'Posting data to tsdb {}'.format(
                        'succeeded' if r.ok else 'failed')
            data = []

if __name__ == '__main__':
    try:
        args = parse_args()

        # create a log directory for this run
        args.logDir = "%s/%s" % (args.logDir, time.time())
        if not os.path.exists(args.logDir):
            os.makedirs(args.logDir)

        # TODO - log additional args
        print ("starting %i users with options:\n"
            "    url: %s\n"
            "    username: %s\n"
            "    headless: %s\n"
            "    workflows: %s\n"
            "    duration: %is\n"
            "    logDir: %s") % (
                args.users, args.url, args.username, "True" if args.headless else "False", args.workflows, args.duration, args.logDir)

        tsdbQueue = mp.Queue()
        tsdbPusher = mp.Process(
                target = pushToTsdb, args = (args.tsdbUrl, tsdbQueue,))
        tsdbPusher.start()

        startTime = time.time()
        processes = []
        died = 0
        userCount = 0
        shouldWork = True

        # if its worktime or there are any processes
        # left working, do work!
        while len(processes) or shouldWork:
            # check for users that died
            toRemove = []
            for p in processes:
                if not p.is_alive():
                    toRemove.append(p)
                    died += 1
                    print colorizeString("%i users died so far, %i currently running" % (died, len(processes)), "DEBUG")

            # remove any dead users
            for p in toRemove:
                processes.remove(p)

            remainingWorkTime = args.duration - (time.time() - startTime)

            # if work should continue, add users to keep process list full
            if shouldWork and len(processes) < args.users:
                # TODO - skill level
                userName = "bob%i" % userCount
                p = mp.Process(target=startUser, args=(
                    userName, args.url, args.username, args.password,
                    args.headless, args.logDir, args.chromedriver,
                    remainingWorkTime, args.workflows, tsdbQueue))
                userCount += 1
                print colorizeString("%s - started user %s" % (time.asctime(), userName), "DEBUG")
                processes.append(p)
                p.start()
                # give xvfb time to grab a display before kicking off
                # a new request
                # prevent all users from logging in at once
                time.sleep(4)

            # is it quittin time yet?
            if remainingWorkTime < 0 and shouldWork:
                shouldWork = False
                print colorizeString("%s - it's quitting time yall. finish what youre doing" % time.asctime(), "DEBUG")

    except:
        traceback.print_exc()

    finally:
        tsdbQueue.put('STOP')
        tsdbQueue.close()
        tsdbQueue.join_thread()
        endTime = time.time()
        print colorizeString("all processes have exited", "DEBUG")
        print colorizeString("start: %s, end: %s" % \
                (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(startTime)),
                    time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(endTime))), "DEBUG")
