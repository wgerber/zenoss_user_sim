import time, traceback
from common import *

TITLE = 'Zenoss: Dashboard'
locator = {'header': '#header',
        "appPortal": "#app-portal"}

@assertPage('title', TITLE)
def checkPageLoaded(user, pushActionStat):
    start = time.time()
    try:
        find(user.driver, locator["appPortal"])
    except:
        raise PageActionException(whoami(),
                "could not find appPortal element",
                screen=e.screen)
    waitTime = time.time() - start
    pushActionStat(whoami(), 'waitTime', waitTime, start)
