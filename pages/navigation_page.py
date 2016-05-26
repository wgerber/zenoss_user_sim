import traceback
from common import *
from pages import DashboardPage

locator = {'events': '#Events-nav-button',
           'infrastructure': '#Infrastructure-nav-button',
           "logoutLink": "#sign-out-link",
           "dashboardLink": "#Dashboard-nav-button"}

@timed
@assertPageAfter('title', 'Zenoss: Events')
def goToEventConsole(user):
    result = Result(whoami())
    start = time.time()
    find(user.driver, locator['events']).click()
    result.putStat("waitTime", time.time() - start)
    return result

@timed
@assertPageAfter('title', 'Zenoss: Dashboard')
def goToDashboard(user):
    result = Result('goToDashboard')
    try:
        find(user.driver, locator['dashboardLink']).click()
    except:
        result.fail("unexpected failure navigating to dashboard")
        traceback.print_exc()

    if not DashboardPage.checkPageLoaded(user):
        result.fail("dashboard page did not load")

    return result

@timed
@assertPageAfter('title', 'Zenoss: Devices')
def goToDevicesPage(user):
    # TODO - handle popup without sleeps
    time.sleep(2) # wait pop-up
    find(user.driver, locator['infrastructure']).click()
    result = ActionResult('goToDevicesPage')
    return result

@timed
@screenshot
@assertPageAfter('title', 'Login')
def logout(user):
    result = ActionResult("logout")

    try:
        time.sleep(3) # Temporary workaround for pop-up on Young's computer
        logout_link = find(user.driver, locator["logoutLink"])
        logout_link.click()
    except:
        # TODO - get details from exception
        result.fail("unexpected failure in logout")
        traceback.print_exc()

    return result
