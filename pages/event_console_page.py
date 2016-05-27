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
@assertPage('title', TITLE)
def filterBySeverity(user, pushActionStat, severity):
    time.sleep(3)
    result = ActionResult(whoami())
    severities = ["critical", "error", "warning", "info", "debug", "clear"]

    actionStart = time.time()

    start = time.time()
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
            # if this is not checked but it should
            # be, then click it
            elif not isChecked and currentSev == severity:
                el.click()
                changedFilter = True

    # if the filter was changed, wait for the event table
    # to go stale
    if changedFilter:
        eventsTable = find(user.driver, elements["eventsTable"])
        wait(user.driver, EC.staleness_of(eventsTable))

    result.putStat("waitTime", time.time() - start)

    waitTime = time.time() - actionStart
    pushActionStat(whoami(), 'waitTime', waitTime, actionStart)
    return result

@timed
@assertPage('title', TITLE)
def sortByLastSeen(user, pushActionStat, newSortDir):
    result = ActionResult(whoami())
    newSortDir = "ASC" if newSortDir == "ascending" else "DESC"
    sortDir = None

    actionStart = time.time()

    start = time.time()

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
        # wait until event table updates
        wait(user.driver, EC.staleness_of(eventsTable))

    result.putStat("waitTime", time.time() - start)
    waitTime = time.time() - actionStart
    pushActionStat(whoami(), 'waitTime', waitTime, actionStart)

    return result

@timed
@assertPage('title', TITLE)
def getEvents(user):
    result = ActionResult('getEvents')

    actionStart = time.time()
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
    waitTime = time.time() - actionStart
    pushActionStat(whoami(), 'waitTime', waitTime, actionStart)

    return result
