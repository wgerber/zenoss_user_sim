import time
from common import *
from pages import LoginPage, EventConsolePage, NavigationPage

class MonitorEvents(Workflow):
    @timed
    @screenshot
    def run(self, user):
        result = WorkflowResult(self.name)
        do = doer(result, user)

        if not user.loggedIn:
            result.fail("user is not logged in")
            return result

        workStart = time.time()
        if not do(NavigationPage.goToEventConsole, (user,)):
            return result
        if not do(EventConsolePage.filterBySeverity, (user, "critical")):
            return result
        if not do(EventConsolePage.sortByLastSeen, (user, "ascending")):
            return result
        result.putStat('workTime', time.time() - workStart)

        """
        # go to event console
        if not do(NavigationPage.goToEventConsole, (user,)):
            return result

        # filter events to critical only
        if not do(EventConsolePage.filterBySeverity, (user, "critical")):
            return result

        # sort events by last seen
        if not do(EventConsolePage.sortByLastSeen, (user, "ascending")):
            return result
            """

        """
        # look at events
        eventResult = takeAction(result, EventConsolePage.getEvents, user)
        result.addActionResult(eventResult)
        if not eventResult.success:
            return result

        # do things with events
        events = eventResult.data["getEvents.events"]
        from pprint import pprint; pprint(events)
        for event in events:
            if user.name in event["summary"]:
                user.log("my name's in that event summary! i should do something!")
                user.think(3)
            user.think(1)
        """

        # stare at the screen REAL hard
        user.think(8)

        # TODO - refresh/filter/sort

        return result

def doer(result, user):
    def fn(actionFn, args):
        # perform action
        actionResult = takeAction(result, actionFn, *args)
        # log success/fail message
        message = ""
        if result.success:
            message += "successfully performed"
        else:
            message += "failed to perform"
        message += " %s" % actionFn.__name__
        elapsed = actionResult.stat["%s.elapsedTime" % actionFn.__name__]
        if elapsed is not None:
            message += " (%is)" % elapsed
        user.log(message)
        return result.success
    return fn
