from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

from common import *

TITLE = 'Zenoss: Devices'
locator = {'ipFilter': '#device_grid-filter-ipAddress-inputEl',
           'deviceRows': "#device_grid-body table .x-grid-row"}

def filterByIp(driver, ip):
    find(driver, locator['ipFilter']).clear()
    find(driver, locator['ipFilter']).send_keys(ip)
    find(driver, locator['ipFilter']).send_keys(Keys.RETURN)

    # Return retrieved list
    try:
        timeout = 10
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, locator['deviceRows'])))
    except TimeoutException:
        print "Device rows did not appear in {} secs.".format(timeout)
        return False

    deviceRows = findMany(driver, locator['deviceRows'])
    devices = []
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


    data = {'devices': devices}

    return {'success': True, 'data': data}


