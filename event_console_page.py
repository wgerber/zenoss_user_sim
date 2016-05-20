import time
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils import assertPage

# TODO: Differentiate EventConsole, EventArchive, etc.
TITLE = 'Zenoss: Events'
locator = {'severityBtn': (By.ID, 'events_grid-filter-severity-btnEl'),
           'selectBtn': (By.ID, 'select-button-btnEl'),
           'ackBtn': (By.ID, 'events_toolbar_ack-btnEl'),
           'refreshBtn': (By.NAME, 'refresh-button'),
           'allMenu': (By.ID, 'menuitem-1063-itemEl'),
           'events': '#events_grid-body table:nth-of-type(1) .x-grid-row',
           'eventStateElement': '.x-grid-cell-eventState',
           'eventState': {'new': '.status-icon-small-new'}}

@assertPage(TITLE)
def filterBySeverity(driver, severity):
    time.sleep(3) # Wait until the pop-up disappears.

    try:
        element = 'severityBtn'
        timeout = 3
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator[element]))
    except TimeoutException:
        print '{} did not appear in {} secs'.format(element, timeout)

    driver.find_element(*locator['severityBtn']).click()

    return True

@assertPage(TITLE)
def selectAll(driver):
    time.sleep(3) # Wait until the pop-up disappears.

    try:
        element = 'selectBtn'
        timeout = 3
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator[element]))
    except TimeoutException:
        print '{} did not appear in {} secs'.format(element, timeout)
        return False

    driver.find_element(*locator['selectBtn']).click()
    driver.find_element(*locator['allMenu']).click()

    return True

@assertPage(TITLE)
def ackAll(driver):
    selectAll(driver)
    driver.find_element(*locator['ackBtn']).click()

    return True

@assertPage(TITLE)
def getEvents(driver):
    try:
        timeout = 10
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, locator['events'])))
    except TimeoutException:
        print "The Events nav button didn't become clickable in {} secs.".format(timeout)
        return False

    find(d, "#events_grid")

    event_rows = findMany(d, "#events_grid-body table .x-grid-row")
    events = []
    for el in event_rows:
        events.append({
            "resource": findIn(el, ".x-grid-cell-device").text,
            "class": findIn(el, ".x-grid-cell-eventClass").text,
            "summary": findIn(el, ".x-grid-cell-summary").text,
            "first_seen": findIn(el, ".x-grid-cell-firstTime").text,
            "last_seen": findIn(el, ".x-grid-cell-lastTime").text,
            "count": findIn(el, ".x-grid-cell-count").text,
        })

    data = {'events': events}

    return {'success': True, 'data': data}
