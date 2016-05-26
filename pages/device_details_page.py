import traceback
from common import *

locator = {'ipFilter': '#device_grid-filter-ipAddress-inputEl',
           'deviceRows': "#device_grid-body table .x-grid-row",
           'navBtns': '#deviceDetailNav-body table .x-grid-row',
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
        if row.text == "Graphs":
            # TODO - handle stale element
            row.click()
            foundGraphs = True
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
        backButtonEl.click()
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
        zoomOutEl.click()
        # TODO - wait till graph updates

    totalWorkTime += time.time() - start

    # just take a minute. just stop and take a minute and think
    user.think(4)

    result.putStat("workTime", totalWorkTime)
    return result

@timed
def viewComponentDetails(user, componentName):
    result = ActionResult(whoami())
    componentRows = _getComponentRows(user)
    totalWorkTime = 0

    start = time.time()
    foundComp = False
    for rowEl in componentRows:
        if rowEl.text == componentName:
            rowEl.click()
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

    result.putStat("workTime", totalWorkTime)
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

def _selectComponentSection(user, sectionName):
    dropdownListItems = []
    try:
        find(user.driver, locator["componentCardDisplayDropdown"]).click()
        dropdownListItems = findMany(user.driver, ".x-boundlist .x-boundlist-item")
    except:
        traceback.print_exc()
        return False

    try:
        for el in dropdownListItems:
            if el.text == sectionName:
                el.click()
                return True
    except StaleElementReferenceException:
        # this seems ridiculous, but if we find stale
        # elements, just uhh... try again :/
        print "hit stale element while looking at dropdown. retrying"
        return _selectComponentSection(user, sectionName)

    print "didnt find '%s' in components display dropdown" % sectionName
    return False


@timed
@assertPage('url', 'devicedetail#deviceDetailNav')
def getEvents(user, sortedBy, ascending):
    result = ActionResult('getEvents')

    time.sleep(3) # pop-up

    navBtns = getNavBtns(user)
    if not navBtns:
        result.success = False
        return result
    navBtns[1].click() # Click the Events button

    find(user.driver, "#device_events")

    try:
        event_rows = findMany(user.driver, "#device_events-body table .x-grid-row")
    except TimeoutException:
        event_rows = []

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

    result.putData('events', events)

    return result

@timed
@assertPage('url', 'devicedetail#deviceDetailNav')
def lookAtGraphs(user):
    result = ActionResult('lookAtGraphs')

    navBtns = getNavBtns(user)
    if not navBtns:
        result.success = False
        return result

    for btn in navBtns:
        if btn.text == 'Graphs':
            btn.click() # Click the Graphs button

            try:
                graphs = find(user.driver, '#device_graphs-body', 20)
                findManyIn(graphs, '.graph-panel')
            except TimeoutException:
                user.log('Timed out while loading device graphs', severity="WARN")
                result.success = False

    return result

@timed
@assertPage('url', 'devicedetail#deviceDetailNav')
def lookAtComponentGraphs(user):
    result = ActionResult('lookAtComponentGraphs')

    # Parse component type texts
    navBtns = getNavBtns(user)
    if not navBtns:
        result.success = False
        return result

    btnTexts = []
    comp = False
    for btn in navBtns:
        if btn.text == 'Graphs':
            comp = False
        if comp:
            btnTexts.append(btn.text)
        if btn.text == 'Components':
            comp = True

    # Iterate through component types and click each item in each type
    for text in btnTexts:
        navBtns = getNavBtns(user)
        if not navBtns:
            result.success = False
            return result
        for btn in navBtns:
            if btn.text == text:
                btn.click()
                rows = findMany(user.driver, '#component_card-body table .x-grid-row')
                for row in rows:
                    # When it clicks through the rows in the Network Routes table,
                    # the link to interface is clicked if no-headless.
                    if btn.text.startswith('Network Routes'):
                        cols = findManyIn(row, '.x-grid-cell')
                        cols[3].click()
                    else:
                        row.click()

                    try:
                        graphs = find(user.driver, '#graph_panel-body', 20)
                        findManyIn(graphs, 'graph-panel')
                    except TimeoutException:
                        result.success = False

                    user.think(3) # TODO: How long would a user think before proceeding?
                break

    return result

def zoomIn(user, times):
    result = ActionResult('zoomIn')

    toolbarBtns = findMany(user.driver, '#device_graphs .x-btn')
    for _ in range(times):
        toolbarBtns[1].click()

    # TODO: Click the refresh btn.

    return result

@assertPage('url', 'devicedetail#deviceDetailNav')
def getNavBtns(user):
    try:
        navBtns = findMany(user.driver, locator['navBtns'])
        return navBtns
    except TimeoutException:
        return None


