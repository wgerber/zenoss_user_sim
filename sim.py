import time
from xvfbwrapper import Xvfb

from pages import *
from workflows import *
from users import *

# TODO - configure from caommand line
headless = False
if headless:
    xvfb = Xvfb(width=1100, height=800)
    xvfb.start()

if __name__ == '__main__':
    # TODO - spin up n users
    # TODO - configure URL, username, pass
    # TODO - configure user
    # TODO - chromedriver location
    bob = User()
    login = LoginAndOut()
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
