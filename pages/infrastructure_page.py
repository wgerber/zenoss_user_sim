import traceback
from common import *

MAX_RETRIES = 3

elements = {
    "deviceGrid": "#device_grid"}

def checkPageReady(user, pushActionStat):
    start = time.time()
    waitWatch = StopWatch().start()
    elapsedWatch = StopWatch().start()
    try:
        find(user.driver, elements["deviceGrid"])
    except Exception as e:
        raise PageActionException(whoami(),
                "could not find deviceGrid element: %s" % e.msg,
                screen=e.screen)
    pushActionStat(whoami(), 'waitTime', waitWatch.total, start)
    pushActionStat(whoami(), 'elapsedTime', elapsedWatch.total, start)
