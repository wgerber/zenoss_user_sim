from common import *

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

def checkPageReady(user, pushActionStat):
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()
    try:
        find(user.driver, locator["deviceDetailNav"])
    except Exception as e:
        raise PageActionException(whoami(),
                "could not find deviceDetailNav element: %s" % e.msg,
                screen=e.screen)
    waitTimer.stop()
    elapsed.stop()

@retry(MAX_RETRIES)
def viewDeviceGraphs(user, pushActionStat):
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()
    rows = []
    try:
        rows = findMany(user.driver, locator["deviceDetailNavRows"])
    except Exception as e:
        raise PageActionException(whoami(),
                "could not find device detail nav rows: %s" % e.msg,
                screen=e.screen)

    foundGraphs = False
    for row in rows:
        try:
            if row.text == "Graphs":
                row.click()
                foundGraphs = True
        except Exception as e:
            raise PageActionException(whoami(),
                    "could not click 'Graph' device nav row: %s" % e.msg,
                    screen=e.screen)

    if not foundGraphs:
        raise PageActionException(whoami(),
                "could not find graphs nav link",
                screen=user.driver.get_screenshot_as_png())

    #wait till at least 1 graph loads
    try:
        find(user.driver, locator["europaGraph"])
    except Exception as e:
        raise PageActionException(whoami(),
                "could not find a single teeny tiny itty bitty graph. Not even one.",
                screen=user.driver.get_screenshot_as_png())

    waitTimer.stop()
    elapsed.stop()

@retry(MAX_RETRIES)
def interactWithDeviceGraphs(user, pushActionStat):
    buttonEls = []
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    think = StatRecorder(pushActionStat, whoami(), "thinkTime");
    elapsed.start()
    waitTimer.start()

    # pan back a few times
    for _ in xrange(4):
        # find graph controls
        try:
            buttonEls = findMany(user.driver, locator["deviceGraphControls"])
        except Exception as e:
            raise PageActionException(whoami(),
                    "could not find device graph controls: %s" % e.msg,
                    screen=e.screen)
        # find the back button
        backButtonEl = [el for el in buttonEls if el.text == "<"][0]
        if not backButtonEl:
            raise PageActionException(whoami(),
                    "could not find device graph back button",
                    screen=user.driver.get_screenshot_as_png())
        # pan back
        try:
            backButtonEl.click()
        except Exception as e:
            raise PageActionException(whoami(),
                    "could not click device graph back button: %s" % e.msg,
                    screen=e.screen)
        # TODO - wait till graph updates

    waitTimer.stop()

    # contemplate life, the universe, and everything
    think.start()
    user.think(4)
    think.stop()

    waitTimer.start()
    # zoom out a few times
    for _ in xrange(2):
        # find graph controls
        try:
            buttonEls = findMany(user.driver, locator["deviceGraphControls"])
        except Exception as e:
            raise PageActionException(whoami(),
                    "could not find device graph controls: %s" % e.msg,
                    screen=e.screen)
        # find the zoom out button
        zoomOutEl = [el for el in buttonEls if el.text == "Zoom Out"][0]
        if not zoomOutEl:
            raise PageActionException(whoami(),
                    "could not find device graph zoom out button",
                    screen=user.driver.get_screenshot_as_png())
        # zoom out
        try:
            zoomOutEl.click()
        except Exception as e:
            raise PageActionException(whoami(),
                    "could not click device graph back button: %s" % e.msg,
                    screen=e.screen)
        # TODO - wait till graph updates

    waitTimer.stop()

    # just take a minute. just stop and take a minute and think
    think.start()
    user.think(4)
    think.stop()

    elapsed.stop()

@retry(MAX_RETRIES)
def viewComponentDetails(user, pushActionStat, componentName):
    componentRows = _getComponentRows(user)

    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    think = StatRecorder(pushActionStat, whoami(), "thinkTime");
    elapsed.start()
    waitTimer.start()

    foundComp = False
    for rowEl in componentRows:
        if rowEl.text == componentName:
            try:
                rowEl.click()
            except Exception as e:
                raise PageActionException(whoami(),
                        "couldnt click component row el: %s" % e.msg,
                        screen=e.screen)
            foundComp = True

    if not foundComp:
        raise PageActionException(whoami(),
                "could not find component named %s" % componentName,
                screen=user.driver.get_screenshot_as_png())

    # wait until component table rows have loaded
    try:
        findMany(user.driver, locator["componentCardTopPanelRows"])
    except Exception as e:
        raise PageActionException(whoami(),
                "no component rows found: %s" % e.msg,
                screen=e.screen)

    _selectComponentSection(user, "Graphs")

    waitTimer.stop()

    # TODO - wait till graphs or "no data" message
    # TODO - interact with graphs
    think.start()
    user.think(4)
    think.stop()

    waitTimer.start()
    _selectComponentSection(user, "Events")

    try:
        find(user.driver, locator["componentCardEventTable"])
    except Exception as e:
        raise PageActionException(whoami(),
                "could not find event table: %s" % e.msg,
                screen=e.screen)


    waitTimer.stop()
    # TODO - ensure event table rows have loaded
    think.start()
    user.think(4)
    think.stop()
    elapsed.stop()

def getComponentNames(user, pushActionStat):
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    elapsed.start()
    waitTimer.start()
    # NOTE - the name includes the component count
    return map(lambda x: x.text, _getComponentRows(user))
    waitTimer.stop()
    elapsed.stop()

def _getComponentRows(user):
    componentRows = []
    try:
        rows = findMany(user.driver, locator["deviceDetailNavRows"])
    except Exception as e:
        raise PageActionException(whoami(),
                "could not find device detail nav rows: %s" % e.msg,
                screen=e.screen)

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

@retry(MAX_RETRIES)
def _selectComponentSection(user, sectionName):
    dropdownListItems = []
    try:
        find(user.driver, locator["componentCardDisplayDropdown"]).click()
        dropdownListItems = findMany(user.driver, ".x-boundlist .x-boundlist-item")
    except Exception as e:
        raise PageActionException(whoami(),
                "could not find our click component 'display' dropdown: %s" % e.msg,
                screen=user.driver.get_screenshot_as_png())

    try:
        for el in dropdownListItems:
            if el.text == sectionName:
                el.click()
                return True
    except StaleElementReferenceException:
        raise PageActionException(whoami(),
                "hit stale element while iterating dropdown",
                screen=user.driver.get_screenshot_as_png())

    raise PageActionException(whoami(),
            "didn't find '%s' in components display dropdown" % sectionName,
            screen=user.driver.get_screenshot_as_png())
