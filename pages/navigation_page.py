import traceback
from common import *

locator = {'events': '#Events-nav-button',
           'infrastructure': '#Infrastructure-nav-button',
           "logoutLink": "#sign-out-link"}

@timed
@assertPageAfter('title', 'Zenoss: Events')
def goToEventConsole(user):
    # TODO - handle popup without sleeps
    time.sleep(2) # Wait until the pop-up disappears.
    find(user.driver, locator['events']).click()
    result = Result('goToEventConsole')
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
