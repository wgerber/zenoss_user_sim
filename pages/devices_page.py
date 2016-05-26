from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

from common import *

TITLE = 'Zenoss: Devices'
locator = {'ipFilter': '#device_grid-filter-ipAddress-inputEl',
           'refreshBtn': '#refreshdevice-button',
           'deviceTable': '#device_grid-body .x-grid-table',
           'deviceRows': "#device_grid-body table .x-grid-row",
           'device': '.z-entity'}

@timed
@assertPage('title', TITLE)
def filterByIp(user, ip):
    result = ActionResult('filterByIp')
    try:
        find(user.driver, locator['ipFilter']).clear()
        find(user.driver, locator['ipFilter']).send_keys(ip)
        find(user.driver, locator['refreshBtn']).click()
    except TimeoutException:
        user.log('Failed to enter Ip address to the text area', severity="WARN")
        result.success = False
        return result

    deviceTable = find(user.driver, locator["deviceTable"])
    try:
        wait(user.driver, EC.staleness_of(deviceTable), 20)
    except TimeoutException:
        user.log('Failed to update the list of devices after filtering', severity="WARN")
        result.success = False
        return result

    devices = []
    try:
        deviceRows = findMany(user.driver, locator['deviceRows'])
        for el in deviceRows:
            trial = 1
            maxTrial = 10
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
                user.log('Filtering by Ip {} reached max trial'.format(ip), severity="WARN")
                result.success = False
                return result
    except TimeoutException:
        if "wait" in find(user.driver, "body").get_attribute("style"):
            result.fail("timed out waiting for event rows")
            return result
    finally:
        result.putData('devices', devices)

    return result

@timed
@assertPageAfter('url', 'devicedetail#deviceDetailNav:device_overview')
def goToDeviceDetailPage(user, ip):
    result = ActionResult('goToDeviceDetailPage')

    actionResult = filterByIp(user, ip)
    if actionResult.data['filterByIp.devices']:
        find(user.driver, locator['device']).click()
        time.sleep(3) # TODO: Wait properly.
    return result
