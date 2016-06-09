from common import *

MAX_EVENT_ROWS = 10

# TODO: Differentiate EventConsole, EventArchive, etc.
TITLE = 'Zenoss: Events'
elements = {"severityBtn": "#events_grid-filter-severity-btnEl",
            "eventsTable": "#events_grid .x-grid-table",
            "lastSeenHeader": "#lastTime",
            "eventRows": '#events_grid-body table:nth-of-type(1) .x-grid-row',
            }

@retry(MAX_RETRIES)
@assertPage('title', TITLE)
def filterBySeverity(user, pushActionStat, severity):
    severities = ["critical", "error", "warning", "info", "debug", "clear"]

    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()
    try:
        find(user.driver, elements["severityBtn"]).click()
    except Exception as e:
        raise PageActionException(whoami(),
                "could not find severity button: %s" % e.msg,
                screen=e.screen)

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

    waitTimer.stop()
    elapsed.stop()

@assertPage('title', TITLE)
def sortByLastSeen(user, pushActionStat, newSortDir):
    newSortDir = "ASC" if newSortDir == "ascending" else "DESC"
    sortDir = None

    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()

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

    waitTimer.stop()
    elapsed.stop()

@retry(MAX_RETRIES)
@assertPage('title', TITLE)
def viewEventDetails(user, pushActionStat, event):
    eventRowEl = _getEventRowEl(user, event)
    if not eventRowEl:
        raise PageActionException(whoami(),
                "could not find event row for event with id %s" % event.evid,
                screen=user.driver.get_screenshot_as_png())
    # TODO - double click row
    # TODO - get details?
    pass

@retry(MAX_RETRIES)
@assertPage('title', TITLE)
def ackEvent(user, pushActionStat, event):
    # TODO - select row
    # TODO - click ack button
    # TODO - verify update?
    pass

def addLogMessageToEvent(user, pushActionStat, event, message):
    # TODO - viewEventDetails
    # TODO - fill log field
    # TODO - click add button
    # TODO - verify added?
    pass

@retry(MAX_RETRIES)
@assertPage('title', TITLE)
def getEvents(user, pushActionStat):
    eventRows = []
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()

    eventRows = _getEventRowEls(user)
    print "fount %i eventRows, only using first %i" % (len(eventRows), MAX_EVENT_ROWS)
    eventRows = eventRows[:MAX_EVENT_ROWS]

    events = []
    try:
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
                    val = severityStatusClass.split(" ")[-1]
                    pass
                event[colName] = val
            events.append(event)
    except StaleElementReferenceException:
        raise PageActionException(whoami(),
                "hit stale element while getting events",
                screen=user.driver.get_screenshot_as_png())

    waitTimer.stop()
    elapsed.stop()
    return events

def _getEventRowEl(user, event):
    """ given an event dict, finds first matching event row el"""
    eventRows = _getEventRowEls(user)
    for eventRow in eventRows:
        # NOTE: assumes event id column is visible
        idCell = findIn(eventRow, ".x-grid-cell-evid")
        if idCell.text == event.evid:
            return eventRow
    return None


def _getEventRowEls(user):
    """ finds all event row elements """
    try:
        return findMany(user.driver, elements["eventRows"])
    # we can timeout because there are no event rows,
    # or we can timeout because the UI is slow to respond
    except TimeoutException:
        # if body has style "cursor: wait", then extjs is loading
        # something, and this is an actual timeout
        if "wait" in find(user.driver, "body").get_attribute("style"):
            raise PageActionException(whoami(),
                    "timed out waiting for event rows",
                    screen=user.driver.get_screenshot_as_png())

