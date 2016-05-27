import traceback
from common import *

MAX_RETRIES = 5

locator = {'navBtns': '#deviceDetailNav-body table .x-grid-row',
           "deviceDetailNav": "#deviceDetailNav",
           "deviceDetailNavRows": "#deviceDetailNav .x-grid-row",
           "europaGraph": ".europagraph",
           "deviceGraphs": "#device_graphs",
           "deviceGraphControls": "#device_graphs .x-btn",
           "componentCard": "#component_card",
           "componentCardTopPanelRows": "#component_card-body>.x-panel:nth-of-type(1) .x-panel-body .x-grid-view .x-grid-row",
           "componentCardDisplayDropdown": "#component_card-body>.x-panel>.x-toolbar .x-form-trigger",
           "componentCardGraphs": "#component_card-body>.x-panel:last-of-type .europagraph",
           "componentCardEventTable": "#component_card-body #event_panel .x-grid-table"}

@timed
def checkPageReady(user):
    result = ActionResult(whoami())
    try:
        find(user.driver, locator["deviceDetailNav"])
    except:
        result.fail("could not find deviceDetailNav element")
    return result

@timed
@retry(MAX_RETRIES)
def viewDeviceGraphs(user):
    result = ActionResult(whoami())

    rows = []
    try:
        rows = findMany(user.driver, locator["deviceDetailNavRows"])
    except:
        result.fail("could not find device detail nav rows")
        return result

    foundGraphs = False
    for row in rows:
        try:
            if row.text == "Graphs":
                row.click()
                foundGraphs = True
                return result
        except:
            result.fail("couldnt click 'Graph' device nav row")
            return result

    if not foundGraphs:
        result.fail("could not find graphs nav link")
        return result

    #wait till at least 1 graph loads
    try:
        find(user.driver, locator["europaGraph"])
    except:
        result.fail("could not find a single teeny tiny itty bitty graph. Not even one")
        return result

    return result

@timed
@retry(MAX_RETRIES)
def interactWithDeviceGraphs(user):
    result = ActionResult(whoami())
    buttonEls = []

    totalWorkTime = 0

    start = time.time()
    # pan back a few times
    for _ in xrange(4):
        # find graph controls
        try:
            buttonEls = findMany(user.driver, locator["deviceGraphControls"])
        except:
            result.fail("could not find device graph controls")
            return result
        # find the back button
        backButtonEl = [el for el in buttonEls if el.text == "<"][0]
        if not backButtonEl:
            result.fail("could not find device graph back button")
            return result
        # pan back
        try:
            backButtonEl.click()
        except:
            result.fail("couldnt click back button el")
            return result
        # TODO - wait till graph updates

    totalWorkTime += time.time() - start

    # contemplate life, the universe, and everything
    user.think(4)

    start = time.time()
    # zoom out a few times
    for _ in xrange(2):
        # find graph controls
        try:
            buttonEls = findMany(user.driver, locator["deviceGraphControls"])
        except:
            result.fail("could not find device graph controls")
            return result
        # find the zoom out button
        zoomOutEl = [el for el in buttonEls if el.text == "Zoom Out"][0]
        if not zoomOutEl:
            result.fail("could not find device graph zoom out button")
            return result
        # zoom out
        try:
            zoomOutEl.click()
        except:
            result.fail("couldnt click zoomoutel")
            return result
        # TODO - wait till graph updates

    totalWorkTime += time.time() - start

    # just take a minute. just stop and take a minute and think
    user.think(4)

    result.putStat("waitTime", totalWorkTime)
    return result

@timed
@retry(MAX_RETRIES)
def viewComponentDetails(user, componentName):
    result = ActionResult(whoami())
    componentRows = _getComponentRows(user)
    totalWorkTime = 0

    start = time.time()
    foundComp = False
    for rowEl in componentRows:
        if rowEl.text == componentName:
            try:
                rowEl.click()
            except:
                result.fail("couldnt click component row el")
                return result
            foundComp = True

    if not foundComp:
        result.fail("could not find component named %s" % componentName)
        return result

    # wait until component table rows have loaded
    try:
        findMany(user.driver, locator["componentCardTopPanelRows"])
    except:
        result.fail("no component rows found")
        return result

    if not _selectComponentSection(user, "Graphs"):
        result.fail("could not view component graphs")
        return result

    totalWorkTime += time.time() - start

    # TODO - wait till graphs or "no data" message
    # TODO - interact with graphs
    user.think(4)

    start = time.time()

    if not _selectComponentSection(user, "Events"):
        result.fail("could not view component events")
        return result

    try:
        find(user.driver, locator["componentCardEventTable"])
    except:
        result.fail("could not find event table")
        return result

    totalWorkTime += time.time() - start

    # TODO - ensure event table rows have loaded
    user.think(4)

    result.putStat("waitTime", totalWorkTime)
    return result

def getComponentNames(user):
    # NOTE - the name includes the component count
    return map(lambda x: x.text, _getComponentRows(user))

def _getComponentRows(user):
    componentRows = []
    try:
        rows = findMany(user.driver, locator["deviceDetailNavRows"])
    except:
        result.fail("could not find device detail nav rows")
        return result

    # NOTE - assumes graphs comes immediately after components
    foundComps = False
    for row in rows:
        if row.text == "Graphs":
            break
        if row.text == "Components":
            foundComps = True
            continue
        if foundComps:
            componentRows.append(row)
    return componentRows

# TODO - adjust @retry decorator to work
# with this function that doesnt return result instance
def _selectComponentSection(user, sectionName, attempt=0):
    if attempt >= MAX_RETRIES:
        user.log("gave up looking for %s in details dropdown" % sectionName)
        return False
    dropdownListItems = []
    try:
        find(user.driver, locator["componentCardDisplayDropdown"]).click()
        dropdownListItems = findMany(user.driver, ".x-boundlist .x-boundlist-item")
    except:
        user.log("%s problem finding or clicking or something on attempt %i" % (user.name, attempt))
        return _selectComponentSection(user, sectionName, attempt=attempt+1)

    try:
        for el in dropdownListItems:
            if el.text == sectionName:
                el.click()
                return True
    except StaleElementReferenceException:
        # this seems ridiculous, but if we find stale
        # elements, just uhh... try again :/
        user.log("%s hit stale element while looking at dropdown on attempt %i" % (user.name, attempt))
        return _selectComponentSection(user, sectionName, attempt=attempt+1)

    user.log("%s didnt find '%s' in components display dropdown on attempt %i" % (user.name, sectionName, attempt))
    return _selectComponentSection(user, sectionName, attempt=attempt+1)
