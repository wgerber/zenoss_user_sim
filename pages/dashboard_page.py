import time
from common import assertPage, ActionResult, whoami

TITLE = 'Zenoss: Dashboard'
locator = {'header': '#header',
        "appPortal": "#app-portal"}

@assertPage('title', TITLE)
def checkPageLoaded(user):
    result = ActionResult(whoami())
    start = time.time()
    try:
        find(user.driver, locator["appPortal"])
    except:
        result.fail("could not find appPortal element")
    result.putStat("waitTime", time.time() - start)
    return result
