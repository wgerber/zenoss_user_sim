from common import *
from pages import DashboardPage, InfrastructurePage

locator = {'events': '#Events-nav-button',
           'infrastructure': '#Infrastructure-nav-button',
           "logoutLink": "#sign-out-link",
           "dashboardLink": "#Dashboard-nav-button"}

@retry(3)
@assertPageAfter('title', 'Zenoss: Events')
def goToEventConsole(user, pushActionStat):
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    waitTimer.start()
    elapsed.start()
    try:
        find(user.driver, locator['events']).click()
    except Exception as e:
        raise PageActionException(whoami(),
                "unexpected failure navigating to event console: %s" % e.msg,
                screen=e.screen)
    # TODO - make sure page is loaded/ready
    waitTimer.stop()
    elapsed.stop()

@retry(3)
@assertPageAfter('title', 'Zenoss: Dashboard')
def goToDashboard(user, pushActionStat):
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    waitTimer.start()
    elapsed.start()
    try:
        find(user.driver, locator['dashboardLink']).click()
    except Exception as e:
        raise PageActionException(whoami(),
                "unexpected failure navigating to dashboard: %s" % e.msg,
                screen=e.screen)

    DashboardPage.checkPageReady(user, pushActionStat)

    waitTimer.stop()
    elapsed.stop()

@retry(3)
@assertPageAfter('title', 'Zenoss: Devices')
def goToDevicesPage(user, pushActionStat):
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    waitTimer.start()
    elapsed.start()
    try:
        find(user.driver, locator['infrastructure']).click()
    except Exception as e:
        raise PageActionException(whoami(),
                "unexpected failure navigating to device page: %s" % e.msg,
                screen=e.screen)

    InfrastructurePage.checkPageReady(user, pushActionStat)

    waitTimer.stop()
    elapsed.stop()

@assertPageAfter('title', 'Login')
def logout(user, pushActionStat):
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    waitTimer.start()
    elapsed.start()
    try:
        find(user.driver, locator['logoutLink']).click()
    except Exception as e:
        raise PageActionException(whoami(),
                "unexpected failure during logout: %s" % e.msg,
                screen=e.screen)
    # TODO - make sure page is loaded/ready
    waitTimer.stop()
    elapsed.stop()
