from common import *

TITLE = 'Zenoss: ' # TODO: Fina a unique attribute of this page
locator = {'ipFilter': '#device_grid-filter-ipAddress-inputEl',
           'deviceRows': "#device_grid-body table .x-grid-row"}

@timed
@assertPage(TITLE)
def getEvents(user, sortedBy, ascending):
    result = ActionResult('getEvents')

    time.sleep(3) # pop-up

    navButtons = findMany(user.driver, '#deviceDetailNav-body table .x-grid-row')
    navButtons[1].click() # Click the Events button

    find(user.driver, "#device_events")

    event_rows = findMany(user.driver, "#device_events-body table .x-grid-row")
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
def lookAtGraphs(user):
    result = ActionResult('lookAtGraphs')

    navButtons = findMany(user.driver, '#deviceDetailNav-body table .x-grid-row')
    navButtons[8].click() # Click the Graphs button

    return result
