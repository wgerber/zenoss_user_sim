import time
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

from common import *

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

elements = {"severityBtn": "#events_grid-filter-severity-btnEl",
            "eventsTable": "#events_grid .x-grid-table",
            "lastSeenHeader": "#lastTime",
            "eventRows": '#events_grid-body table:nth-of-type(1) .x-grid-row',
            }

@timed
@assertPage(TITLE)
def filterBySeverity(user, severity):
    result = ActionResult(whoami())
    severities = ["critical", "error", "warning", "info", "debug", "clear"]
    time.sleep(3) # Wait until the pop-up disappears.

    # TODO - handle exceptions
    sevButton = find(user.driver, elements["severityBtn"])
    sevButton.click()

    # NOTE - assumes just one x-menu is visible
    sevEls = findMany(user.driver, ".x-menu .x-menu-item")

    changedFilter = False
    for el in sevEls:
        currentSev = el.text.strip().lower()
        # ensure this is an actual severity menu item
        if currentSev in severities:
            isChecked = False if ("unchecked" in el.get_attribute("class")) else True
            # if this is checked and it should not be,
            # click it to uncheck it
            if isChecked and currentSev != severity:
                el.click()
                changedFilter = True
                user.think(1)
            # if this is not checked but it should
            # be, then click it
            elif not isChecked and currentSev == severity:
                el.click()
                changedFilter = True
                user.think(1)

    # if the filter was changed, wait for the event table
    # to go stale
    if changedFilter:
        eventsTable = find(user.driver, elements["eventsTable"])
        wait(user.driver, EC.staleness_of(eventsTable), 20)

    return result

@timed
@assertPage(TITLE)
def sortByLastSeen(user, newSortDir):
    result = ActionResult(whoami())
    newSortDir = "ASC" if newSortDir == "ascending" else "DESC"
    sortDir = None

    # TODO - break this after n seconds
    while sortDir != newSortDir:
        header = find(user.driver, elements["lastSeenHeader"])
        headerClass = header.get_attribute("class")
        if "x-column-header-sort" in headerClass:
            headerSortClass = [x for x in headerClass.split(" ") if x.startswith("x-column-header-sort-")][0]
            sortDir = headerSortClass.replace("x-column-header-sort-", "")
            if sortDir == "null":
                sortDir = None
        eventsTable = find(user.driver, elements["eventsTable"])
        header.click()
        user.think(1)
        # wait until event table updates
        wait(user.driver, EC.staleness_of(eventsTable))

    return result

@assertPage(TITLE)
def selectAllEvents(user):
    result = ActionResult('ackAll')
    start = time.time()

    time.sleep(3) # Wait until the pop-up disappears.

    try:
        element = 'selectBtn'
        timeout = 3
        WebDriverWait(user.driver, timeout).until(
            EC.presence_of_element_located(locator[element]))
    except TimeoutException:
        print '{} did not appear in {} secs'.format(element, timeout)
        result.success = False
        return result

    ActionChains(user.driver).key_down(Keys.CONTROL) \
        .send_keys('a').key_up(Keys.CONTROL).perform()

    return result

@assertPage(TITLE)
def ackAll(user):
    result = ActionResult('ackAll')
    start = time.time()

    selectAllEvents(user)
    user.driver.find_element(*locator['ackBtn']).click()

    elapsedTime = time.time() - start

    result.putStat('elapsedTime', elapsedTime)
    return result

@timed
@assertPage(TITLE)
def getEvents(user):
    result = ActionResult('getEvents')

    eventRows = []
    try:
        eventRows = findMany(user.driver, elements["eventRows"])
    # we can timeout because there are no event rows,
    # or we can timeout because the UI is slow to respond
    except TimeoutException:
        # if body has style "cursor: wait", then extjs is loading
        # something, and this is an actual timeout
        if "wait" in find(user.driver, "body").get_attribute("style"):
            result.fail("timed out waiting for event rows")
            return result

    events = []
    for el in eventRows:
        cells = findManyIn(el, ".x-grid-cell")
        event = {}
        for cell in cells:
            colNameClass = [x for x in cell.get_attribute("class").split(" ") if x.startswith("x-grid-cell-")][0]
            colName = colNameClass.replace("x-grid-cell-", "")
            val = cell.text
            # some columns require more work to get useful data
            if colName == "eventState":
                eventStatusClass = findIn(cell, ".x-grid-cell-inner div:nth-of-type(1)").get_attribute("class")
                val = eventStatusClass.split("-")[-1]
            elif colName == "severity":
                severityStatusClass = findIn(cell, ".severity-icon-small").get_attribute("class")
                val = eventStatusClass.split(" ")[-1]
                pass
            event[colName] = val
        events.append(event)

    result.putData('events', events)

    return result
