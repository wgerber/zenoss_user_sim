from common import *

locator = {'events': '#Events-nav-button',
           'infrastructure': '#Infrastructure-nav-button'}

@assertPageAfter('Zenoss: Events')
def goToEventConsole(driver):
    time.sleep(3) # Wait until the pop-up disappears.
    find(driver, locator['events']).click()

    return {'success': True, 'data': None}

    # wait until the page is loaded.
    # check the page is actually event console.
    # If not, return false.

@assertPageAfter('Zenoss: Devices')
def goToDevicesPage(driver):
    time.sleep(2) # wait pop-up
    find(driver, locator['infrastructure']).click()
    # TODO: check the page is loaded.
    return {'success': True, 'data': None}
