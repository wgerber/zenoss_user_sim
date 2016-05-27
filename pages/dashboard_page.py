import time, traceback
from common import assertPage, ActionResult, whoami, find

TITLE = 'Zenoss: Dashboard'
locator = {'header': '#header',
        "appPortal": "#app-portal"}

@assertPage('title', TITLE)
def checkPageLoaded(user, pushActionStat):
    result = ActionResult(whoami())
    start = time.time()
    try:
        find(user.driver, locator["appPortal"])
    except:
        result.fail("could not find appPortal element")
        traceback.print_exc()
    waitTime = time.time() - start
    result.putStat("waitTime", waitTime)
    pushActionStat(whoami(), 'waitTime', waitTime, start)
    return result
