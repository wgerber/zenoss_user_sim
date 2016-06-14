import random
from selenium.webdriver.common.action_chains import ActionChains
from common import *

MAX_EVENT_ROWS = 10

# TODO: Differentiate EventConsole, EventArchive, etc.
TITLE = 'Zenoss: Events'
elements = {"severityBtn": "#events_grid-filter-severity-btnEl",
            "statusBtn": "#events_grid-filter-eventState-btnEl",
            "eventsTable": "#events_grid .x-grid-table",
            "lastSeenHeader": "#lastTime",
            "eventRows": '#events_grid-body table:nth-of-type(1) .x-grid-row',
            "ackBtn": "#events_toolbar_ack",
            "closeBtn": "#events_toolbar_close_events",
            "eventDetails": "#detail_panel",
            "eventDetailRows": ".proptable tr",
            "eventDetailKey": ".proptable_key",
            "eventDetailValue": ".proptable_value",
            "logMessageInput": "#detail-logform-message-inputEl",
            "logMessageSubmit": "#log-container button",
            "logHistory": "#evdetail_log-body table"
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

@retry(MAX_RETRIES)
@assertPage('title', TITLE)
def filterByStatus(user, pushActionStat, statuses):
    ALL_STATUSES = ["new", "acknowledged", "suppressed", "closed", "cleared", "aged"]

    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()
    try:
        find(user.driver, elements["statusBtn"]).click()
    except Exception as e:
        raise PageActionException(whoami(),
                "could not find status button: %s" % e.msg,
                screen=e.screen)

    # NOTE - assumes just one x-menu is visible
    sevEls = findMany(user.driver, ".x-menu .x-menu-item")

    changedFilter = False
    for el in sevEls:
        currentStatus = el.text.strip().lower()
        # ensure this is an actual status menu item
        if currentStatus in ALL_STATUSES:
            isChecked = False if ("unchecked" in el.get_attribute("class")) else True
            # if this is checked and it should not be,
            # click it to uncheck it
            if isChecked and currentStatus not in statuses:
                el.click()
                changedFilter = True
            # if this is not checked but it should
            # be, then click it
            elif not isChecked and currentStatus in statuses:
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
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()
    try:
        el = _getEventRowEl(user, event)
        ActionChains(user.driver).double_click(el).perform()
    except WebDriverException as e:
        raise PageActionException(whoami(),
                "could not view event details for event %s: %s" % (event, e.msg),
                screen=e.screen)
    except Exception as e:
        raise PageActionException(whoami(),
                "could not view event details for event %s: %s" % (event, e.args),
                screen=None)

    try:
        detailsEl = find(user.driver, elements["eventDetails"])
        detailRows = findManyIn(detailsEl, elements["eventDetailRows"])
        details = {}
        for row in detailRows:
            key = findIn(row, elements["eventDetailKey"]).text
            val = findIn(row, elements["eventDetailValue"]).text
            details[key] = val
    except Exception as e:
        raise PageActionException(whoami(),
                "could not gather details for %s: %s" % (event, str(e)),
                screen=None)

    waitTimer.stop()
    elapsed.stop()
    return details

@retry(MAX_RETRIES)
@assertPage('title', TITLE)
def ackEvent(user, pushActionStat, event):
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()
    try:
        _getEventRowEl(user, event).click()
        find(user.driver, elements["ackBtn"]).click()
    except WebDriverException as e:
        raise PageActionException(whoami(),
                "could not ack event %s: %s" % (event, e.msg),
                screen=e.screen)
    except Exception as e:
        raise PageActionException(whoami(),
                "could not ack event %s: %s" % (event, e),
                screen=None)

    # TODO - verify ack was successful?
    waitTimer.stop()
    elapsed.stop()

@retry(MAX_RETRIES)
@assertPage('title', TITLE)
def closeEvent(user, pushActionStat, event):
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()
    try:
        _getEventRowEl(user, event).click()
        find(user.driver, elements["closeBtn"]).click()
    except WebDriverException as e:
        raise PageActionException(whoami(),
                "could not close event %s: %s" % (event, e.msg),
                screen=e.screen)
    except Exception as e:
        raise PageActionException(whoami(),
                "could not close event %s: %s" % (event, e),
                screen=None)

    # TODO - verify ack was successful?
    waitTimer.stop()
    elapsed.stop()

@retry(MAX_RETRIES)
@assertPage('title', TITLE)
def addLogMessageToEvent(user, pushActionStat, event, message=None):
    messages = [
            "Three men were swept up by the flabby claws before anybody turned",
            "The stars were right again, and ravening for delight.",
            "There is a sense of spectral whirling through liquid gulfs of infinity, of dizzying rides through reeling universes on a comets tail, and of hysterical plunges from the newly opened depths was intolerable, and at length the quick-eared Hawkins thought he heard a nasty, slopping sound down there.",
            "Parker slipped as the Alert under way.",
            "Steam had not given out yet.",
            "In this phantasy of prismatic distortion it moved anomalously in a diagonal way, so that all the rules of matter and perspective seemed upset.",
            "- the scattered plasticity of that charnel shore that was not of earth the titan Thing from the stars slavered and gibbered like Polypheme cursing the fleeing ship of Odysseus.",
            "The Thing of the clouds about his consciousness.",
            "Everyone listened, and everyone was listening still when It lumbered slobberingly into sight and gropingly squeezed Its gelatinous green immensity through the black doorway into the shrunken and gibbous sky on flapping membraneous wings.",
            "A mountain walked or stumbled.",
            "Knowing that the chronicler could not put on paper.",
            "There was a bursting as of an exploding bladder, a slushy nastiness as of a daemon galleon.",
            "Death would be a boon if only it could blot out the memories.",
            "The stars were right again, and ravening for delight.",
            "Everyone listened, and everyone watched the queer recession of the distorted, hilarious elder gods and the green, sticky spawn of the stars, had awaked to claim his own.",
            "There was a mighty eddying and foaming in the cabin whilst Johansen was wandering deliriously.",
            "Then came the storm of April 2nd, and a sound that the chronicler could not put on paper.",
            "the scattered plasticity of that dream came rescue-the Vigilant, the vice-admiralty court, the streets of Dunedin, and the laughing maniac by his side.",
            "The Thing of the distorted, hilarious elder gods and the green, bat-winged mocking imps of Tartarus."]
    if not message:
        message = random.choice(messages)

    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()

    # TODO - only call this if event details are not visible
    viewEventDetails(user, pushActionStat, event)
    logHistoryEl = None
    try:
        message = "I investigated this event and found the problem was %s" % message
        logHistoryEl = find(user.driver, elements["logHistory"])
        find(user.driver, elements["logMessageInput"]).send_keys(message)
        find(user.driver, elements["logMessageSubmit"]).click()
    except Exception as e:
        raise PageActionException(whoami(),
                "could not add log message to event %s: %s" % (event, e),
                screen=None)

    # wait till log history is updated with new log message
    wait(user.driver, EC.staleness_of(logHistoryEl))

    waitTimer.stop()
    elapsed.stop()

@retry(MAX_RETRIES)
@assertPage('title', TITLE)
@assertPageAfter('url', 'zport/dmd/Devices')
def goToEventResource(user, pushActionStat, event):
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()
    try:
        rowEl = _getEventRowEl(user, event)
        findIn(rowEl, ".x-grid-cell-device").click()
    except WebDriverException as e:
        raise PageActionException(whoami(),
                "could not click resource link for event %s: %s" % (event, e.msg),
                screen=e.screen)
    except Exception as e:
        raise PageActionException(whoami(),
                "could not click resource link for event %s: %s" % (event, e),
                screen=None)

    # TODO - verify navigate was successful?
    waitTimer.stop()
    elapsed.stop()


@retry(MAX_RETRIES)
@assertPage('title', TITLE)
def getEvents(user, pushActionStat):
    eventRows = []
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");

    currEventRow = find(user.driver, elements["eventRows"])
    nextEventRow = None

    # measure only how long it takes to find the first row.
    # all subsequent row lookups are just selenium/chrome
    # queries we dont care about
    waitTimer.stop()
    elapsed.stop()

    # TODO - while there are event rows
    while(True):
        currEvent = {}
        try:
            # create event dict
            cells = findManyIn(currEventRow, ".x-grid-cell")
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
                currEvent[colName] = val

            # get a reference to the next row for the next tick
            nextEventRow = currEventRow.find_element_by_xpath("following-sibling::*[1]")
            # TODO - store nextEventRow's evid so that if it goes
            # stale, we can find it later
        except StaleElementReferenceException:
            raise PageActionException(whoami(),
                    "hit stale element while getting events",
                    screen=user.driver.get_screenshot_as_png())

        yield currEvent

        # hey lets do this again!
        # TODO - ensure nextEventRow element is not stale
        currEventRow = nextEventRow

def _getEventRowEl(user, event):
    """ given an event dict, finds first matching event row el"""
    eventRows = _getEventRowEls(user)
    for eventRow in eventRows:
        # NOTE: assumes event id column is visible
        idCell = findIn(eventRow, ".x-grid-cell-evid")
        if idCell.text == event["evid"]:
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

