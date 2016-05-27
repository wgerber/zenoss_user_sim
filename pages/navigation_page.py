import traceback
from common import *
from pages import DashboardPage

locator = {'events': '#Events-nav-button',
           'infrastructure': '#Infrastructure-nav-button',
           "logoutLink": "#sign-out-link",
           "dashboardLink": "#Dashboard-nav-button"}

@timed
@retry(3)
@assertPageAfter('title', 'Zenoss: Events')
def goToEventConsole(user):
    result = Result(whoami())
    start = time.time()
    try:
        find(user.driver, locator['events']).click()
    except:
        result.fail("unexpected failure navigating to event console")
        traceback.print_exc()
        return result
    # TODO - make sure page is loaded/ready
    result.putStat("waitTime", time.time() - start)
    return result

@timed
@retry(3)
@assertPageAfter('title', 'Zenoss: Dashboard')
def goToDashboard(user):
    result = Result(whoami())
    start = time.time()
    try:
        find(user.driver, locator['dashboardLink']).click()
    except:
        result.fail("unexpected failure navigating to dashboard")
        traceback.print_exc()
        return result
    if not DashboardPage.checkPageLoaded(user):
        result.fail("dashboard page did not load")
    result.putStat("waitTime", time.time() - start)
    return result

@timed
@retry(3)
@assertPageAfter('title', 'Zenoss: Devices')
def goToDevicesPage(user):
    result = Result(whoami())
    start = time.time()
    try:
        find(user.driver, locator['infrastructure']).click()
    except:
        result.fail("unexpected failure navigating to device page")
        traceback.print_exc()
        return result
    # TODO - make sure page is loaded/ready
    result.putStat("waitTime", time.time() - start)
    return result

@timed
@retry(3)
@screenshot
@assertPageAfter('title', 'Login')
def logout(user):
    result = Result(whoami())
    start = time.time()
    try:
        find(user.driver, locator['logoutLink']).click()
    except:
        result.fail("unexpected failure during logout")
        traceback.print_exc()
        return result
    # TODO - make sure page is loaded/ready
    result.putStat("waitTime", time.time() - start)
    return result
