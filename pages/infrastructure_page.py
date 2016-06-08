from common import *

elements = {
    "deviceGrid": "#device_grid"}

def checkPageReady(user, pushActionStat):
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()
    try:
        find(user.driver, elements["deviceGrid"])
    except Exception as e:
        raise PageActionException(whoami(),
                "could not find deviceGrid element: %s" % e.msg,
                screen=e.screen)
    waitTimer.stop()
    elapsed.stop()
