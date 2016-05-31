import time
from common import *
from pages import LoginPage, EventConsolePage, NavigationPage

class MonitorEvents(Workflow):
    def run(self, user, pushActionStat):
        if not user.loggedIn:
            raise WorkflowException(whoami(), "user is not logged in")

        NavigationPage.goToEventConsole(user, pushActionStat)
        EventConsolePage.filterBySeverity(user, pushActionStat, "critical")
        EventConsolePage.sortByLastSeen(user, pushActionStat, "ascending")

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
