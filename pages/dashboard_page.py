from common import *

TITLE = 'Zenoss: Dashboard'
locator = {'header': '#header',
        "appPortal": "#app-portal"}

@assertPage('title', TITLE)
def checkPageReady(user, pushActionStat):
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()
    try:
        find(user.driver, locator["appPortal"])
    except Exception as e:
        raise PageActionException(whoami(),
                "could not find appPortal element: %s" % e.msg,
                screen=e.screen)
    waitTimer.stop()
    elapsed.stop()
