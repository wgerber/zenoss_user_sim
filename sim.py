import time, traceback, argparse
import pprint
from xvfbwrapper import Xvfb

from workflows import *
from users import *

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
    else:
        return args

def startUser(name, url, username, password, skill, logDir, chromedriver):
    user = User("bob", url=url, username=username, password=password,
            skill=skill, logDir=logDir, chromedriver=chromedriver)

    # TODO - configure workflow
    user.addWorkflow([
        LoginAndLogout(),
        CheckDevice("10.87.128.58"),
        AckEvents()])
    try:
        user.work()
        resultsStr = ""
        for result in user.results:
            resultsStr += pprint.pformat(result.__dict__, indent=4)
            resultsStr += ","
        user.log(resultsStr)
    except:
        user.log("%s unexpectedly failed" % user.name)
        traceback.print_exc()
    finally:
        print "cleaning up"
        user.quit()

if __name__ == '__main__':
    args = parse_args()
    print ("starting %i users with options:\n"
        "    url: %s\n"
        "    username: %s\n"
        "    headless: %s\n"
        "    logDir: %s") % (
            args.users, args.url, args.username, "True" if args.headless else "False", args.logDir)

    if args.headless:
        xvfb = Xvfb(width=1100, height=800)
        xvfb.start()

    # TODO - spin up n users
    # TODO - skill level
    # TODO - workflows
    startUser("bob", args.url, args.username, args.password, ADVANCED, args.logDir, args.chromedriver)

    print "cleaning up"
    if args.headless:
        xvfb.stop()

