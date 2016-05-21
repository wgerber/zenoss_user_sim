import time
from xvfbwrapper import Xvfb

from workflows import *
from users import *

# TODO - configure from command line
ZENOSS_URL = 'https://zenoss5.graveyard.zenoss.loc'
ZENOSS_USERNAME = 'zenny'
ZENOSS_PASSWORD = '*****'
CHROMEDRIVER = '/home/jay/.local/bin/chromedriver'
headless = True

if headless:
    xvfb = Xvfb(width=1100, height=800)
    xvfb.start()

if __name__ == '__main__':
    # TODO - spin up n users
    # TODO - configure user
    bob = User("bob", CHROMEDRIVER)
    login = LoginAndLogout(baseURL=ZENOSS_URL, user=ZENOSS_USERNAME, password=ZENOSS_PASSWORD)
    #ackEvents = AckEvents()
    #bob.addWorkflow([login, ackEvents])
    bob.addWorkflow([login])
    try:
        bob.work()
        print bob.stat
        print bob.results
    except:
        pass
    finally:
        print "cleaning up"
        if headless:
            xvfb.stop()
        bob.quit()
