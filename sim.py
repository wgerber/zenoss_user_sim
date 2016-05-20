import time
from xvfbwrapper import Xvfb

from pages import *
from workflows import *
from users import *

# TODO - configure from command line
ZENOSS_URL = 'https://zenoss5.graveyard.zenoss.loc'
ZENOSS_USERNAME = 'zenny'
ZENOSS_PASSWORD = 'Z3n0ss123'

# TODO - configure from caommand line
headless = False
if headless:
    xvfb = Xvfb(width=1100, height=800)
    xvfb.start()

if __name__ == '__main__':
    # TODO - spin up n users
    # TODO - configure user
    bob = User("bob")
    login = LoginAndOut(baseURL=ZENOSS_URL, user=ZENOSS_USERNAME, password=ZENOSS_PASSWORD)
    bob.addWorkflow([login])
    try:
        bob.work()
        print bob.stat
    except:
        pass
    finally:
        print "cleaning up"
        if headless:
            xvfb.close()
        bob.quit()
