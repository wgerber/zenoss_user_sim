import sys
import time, traceback, argparse
from xvfbwrapper import Xvfb
from multiprocessing import Process

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
        workHour, workflowNames):
    if headless:
        xvfb = Xvfb(width=1100, height=800)
        xvfb.start()

    user = User(name, url=url, username=username, password=password,
            logDir=logDir, chromedriver=chromedriver, workHour=workHour)

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
            user.log('Could not find workflow {}'.format(name))
            user.quit()

        workflows.append(workflowClass())

    workflows.append(LogInOutWorkflow.Logout())

    user.addWorkflow(workflows)

    try:
        user.work()
    except:
        user.log("%s unexpectedly failed" % user.name)
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

if __name__ == '__main__':
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

    processes = []
    for i in xrange(args.users):
        # TODO - skill level
        # TODO - workflows
        p = Process(target=startUser, args=(
            "bob%i"%i, args.url, args.username, args.password, args.headless, args.logDir, args.chromedriver, args.workHour, args.workflows))
        processes.append(p)
        p.start()
        # give xvfb time to grab a display before kicking off
        # a new request
        time.sleep(0.2)
    # TODO - wait till all processes are done and log a message
    for p in processes:
        p.join()
