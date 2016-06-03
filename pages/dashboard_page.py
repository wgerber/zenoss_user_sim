import time, traceback
from common import *

TITLE = 'Zenoss: Dashboard'
locator = {'header': '#header',
        "appPortal": "#app-portal"}

@assertPage('title', TITLE)
def checkPageReady(user, pushActionStat):
    start = time.time()
    try:
        find(user.driver, locator["appPortal"])
    except Exception as e:
        raise PageActionException(whoami(),
                "could not find appPortal element: %s" % e.msg,
                screen=e.screen)
    waitTime = time.time() - start
    pushActionStat(whoami(), 'waitTime', waitTime, start)
