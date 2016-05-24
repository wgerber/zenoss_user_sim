from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

from common import *

TITLE = 'Zenoss: Devices'
locator = {'ipFilter': '#device_grid-filter-ipAddress-inputEl',
           'refreshBtn': '#refreshdevice-button',
           'deviceRows': "#device_grid-body table .x-grid-row",
           'device': '.z-entity'}

@timed
def filterByIp(user, ip):
    result = ActionResult('filterByIp')
    try:
        find(user.driver, locator['ipFilter']).clear()
        find(user.driver, locator['ipFilter']).send_keys(ip)
        find(user.driver, locator['refreshBtn']).click()
    except TimeoutException:
        result.success = False
        return result

    deviceRows = find(user.driver, locator["deviceRows"])
    try:
        wait(user.driver, EC.staleness_of(deviceRows), DEFAULT_TIMEOUT)
    except TimeoutException:
        user.log('Failed to update the list of devices after filtering')
        result.success = False
        return result

    devices = []
    try:
        deviceRows = findMany(user.driver, locator['deviceRows'])
        for el in deviceRows:
            trial = 1
            maxTrial = 3
            while trial <= maxTrial:
                try:
                    devices.append({
                       "name": findIn(el, ".x-grid-cell-name").text,
                       "snmpSysName": findIn(el, ".x-grid-cell-snmpSysName").text,
                       "productionState": findIn(el, ".x-grid-cell-productionState").text,
                       "serialNumber": findIn(el, ".x-grid-cell-serialNumber").text,
                       "priority": findIn(el, ".x-grid-cell-priority").text,
                       "worstevents": findIn(el, ".x-grid-cell-worstevents").text,
                    })
                    break
                except StaleElementReferenceException:
                    trial += 1
                    devices = []
            if trial > maxTrial:
                user.log('Filtering by Ip {} reached max trial'.format(ip))
                result.success = False
                return result
    except TimeoutException:
        # TODO: What if it timed out because the page loading is too slow?
        devices = []
    finally:
        result.putData('devices', devices)

    return result

@timed
def goToDeviceDetailPage(user, ip):
    result = ActionResult('goToDeviceDetailPage')

    actionResult = filterByIp(user, ip)
    if actionResult.data['filterByIp.devices']:
        find(user.driver, locator['device']).click()
        time.sleep(3) # TODO: Wait properly.
        # TODO: Assert device detail page properly.
    return result
