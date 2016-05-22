import time, traceback
import pprint
from xvfbwrapper import Xvfb

from workflows import *
from users import *

# TODO - configure from command line
ZENOSS_URL = 'https://zenoss5.graveyard.zenoss.loc'
ZENOSS_USERNAME = 'zenny'
ZENOSS_PASSWORD = '***'
CHROMEDRIVER = '/home/jay/.local/bin/chromedriver'
LOG_DIR = "/home/jay/tmp"
headless = True

if headless:
    xvfb = Xvfb(width=1100, height=800)
    xvfb.start()

if __name__ == '__main__':
    # TODO - spin up n users
    bob = User("bob", url=ZENOSS_URL, username=ZENOSS_USERNAME, password=ZENOSS_PASSWORD,
            skill=ADVANCED, logDir=LOG_DIR, chromedriver=CHROMEDRIVER)
    bob.addWorkflow([
        LoginAndLogout(),
        CheckDevice("10.87.128.58"),
        AckEvents()])
    try:
        bob.work()
        resultsStr = ""
        for result in bob.results:
            resultsStr += pprint.pformat(result.__dict__, indent=4)
            resultsStr += ","
        bob.log(resultsStr)
    except:
        bob.log("unexpected failure running work")
        traceback.print_exc()
    finally:
        print "cleaning up"
        if headless:
            xvfb.stop()
        bob.quit()
