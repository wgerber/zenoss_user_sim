import time, traceback
from pprint import pprint
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
    bob = User("bob", skill=ADVANCED, logDir=LOG_DIR, chromedriver=CHROMEDRIVER)
    login = LoginAndLogout(baseURL=ZENOSS_URL, user=ZENOSS_USERNAME, password=ZENOSS_PASSWORD)
    #ackEvents = AckEvents()
    #bob.addWorkflow([login, ackEvents])
    bob.addWorkflow([login])
    try:
        bob.work()
        bob.log("all workflows complete")
        print bob.stat
        for result in bob.results:
            pprint(result)
    except:
        bob.log("unexpected failure running work")
        traceback.print_exc()
    finally:
        print "cleaning up"
        if headless:
            xvfb.stop()
        bob.quit()
