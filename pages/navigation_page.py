import traceback
from common import *
from pages import DashboardPage

locator = {'events': '#Events-nav-button',
           'infrastructure': '#Infrastructure-nav-button',
           "logoutLink": "#sign-out-link",
           "dashboardLink": "#Dashboard-nav-button"}

@retry(3)
@assertPageAfter('title', 'Zenoss: Events')
def goToEventConsole(user, pushActionStat):
    start = time.time()
    try:
        find(user.driver, locator['events']).click()
    except Exception as e:
        raise PageActionException(whoami(),
                "unexpected failure navigating to event console",
                screen=e.screen)
    # TODO - make sure page is loaded/ready
    waitTime = time.time() - start
    pushActionStat(whoami(), 'waitTime', waitTime, start)

@retry(3)
@assertPageAfter('title', 'Zenoss: Dashboard')
def goToDashboard(user, pushActionStat):
    start = time.time()
    try:
        find(user.driver, locator['dashboardLink']).click()
    except Exception as e:
        raise PageActionException(whoami(),
                "unexpected failure navigating to dashboard",
                screen=e.screen)

    DashboardPage.checkPageLoaded(user, pushActionStat)

    waitTime = time.time() - start
    pushActionStat(whoami(), 'waitTime', waitTime, start)

@retry(3)
@assertPageAfter('title', 'Zenoss: Devices')
def goToDevicesPage(user, pushActionStat):
    start = time.time()
    try:
        find(user.driver, locator['infrastructure']).click()
    except:
        raise PageActionException(whoami(),
                "unexpected failure navigating to device page",
                screen=e.screen)
    # TODO - make sure page is loaded/ready
    waitTime = time.time() - start
    pushActionStat(whoami(), 'waitTime', waitTime, start)

@retry(3)
@assertPageAfter('title', 'Login')
def logout(user, pushActionStat):
    start = time.time()
    try:
        find(user.driver, locator['logoutLink']).click()
    except:
        raise PageActionException(whoami(),
                "unexpected failure during logout",
                screen=e.screen)
    # TODO - make sure page is loaded/ready
    waitTime = time.time() - start
    pushActionStat(whoami(), 'waitTime', waitTime, start)
