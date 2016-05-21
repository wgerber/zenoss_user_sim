from common import *

locator = {'events': '#Events-nav-button',
           'infrastructure': '#Infrastructure-nav-button'}

@assertPageAfter('Zenoss: Events')
def goToEventConsole(driver):
    start = time.time()
    time.sleep(3) # Wait until the pop-up disappears.
    find(driver, locator['events']).click()
    time.sleep(3)

    result = Result('goToEventConsole')
    elapsedTime = time.time() - start
    result.putStat('elapsedTime', elapsedTime)

    return result

@assertPageAfter('Zenoss: Devices')
def goToDevicesPage(driver):
    start = time.time()
    time.sleep(2) # wait pop-up
    find(driver, locator['infrastructure']).click()

    result = Result('goToDevicePage')
    elapsedTime = time.time() - start
    result.putStat('elapsedTime', elapsedTime)

    return result
