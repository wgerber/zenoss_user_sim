import traceback
from common import *

locator = {'events': '#Events-nav-button',
           'infrastructure': '#Infrastructure-nav-button',
           "logoutLink": "#sign-out-link"}

@assertPageAfter('Zenoss: Events')
def goToEventConsole(user):
    start = time.time()
    time.sleep(3) # Wait until the pop-up disappears.
    find(user.driver, locator['events']).click()
    time.sleep(3)

    result = Result('goToEventConsole')
    elapsedTime = time.time() - start
    result.putStat('elapsedTime', elapsedTime)

    return result

@timed
@assertPageAfter('Zenoss: Devices')
def goToDevicesPage(user):
    # TODO - use clean workaround
    time.sleep(2) # wait pop-up
    find(user.driver, locator['infrastructure']).click()

    result = ActionResult('goToDevicesPage')

    return result

@timed
@assertPageAfter('Login')
def logout(user):
    result = ActionResult("logout")

    try:
        time.sleep(3) # Temporary workaround for pop-up on Young's computer
        logout_link = find(user.driver, locator["logoutLink"])
        logout_link.click()
    except:
        screen = user.screenshot("logout")
        # TODO - get details from exception
        result.fail("unexpected failure in logout. screenshot saved as %s" % screen) 
        traceback.print_exc()

    return result
