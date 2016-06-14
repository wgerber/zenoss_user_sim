import time
from common import *
from pages import LoginPage, EventConsolePage, NavigationPage
from workflows import InvestigateCurrentDevice

class CloseEvents(Workflow):
    def run(self, user, pushActionStat):
        if not user.loggedIn:
            raise WorkflowException(whoami(), "user is not logged in")

        NavigationPage.goToEventConsole(user, pushActionStat)
        EventConsolePage.filterBySeverity(user, pushActionStat, "critical")
        EventConsolePage.filterByStatus(user, pushActionStat, ["new", "acknowledged"])
        EventConsolePage.sortByLastSeen(user, pushActionStat, "ascending")

        # TODO - explicitly turn on event id column
        events = EventConsolePage.getEvents(user, pushActionStat)

        for event in events:
            if event["severity"] == "critical" and event["eventState"] != "acknowledged":
                print "oh snap, unacknowledged crit event %s!" % event["evid"]
                EventConsolePage.ackEvent(user, pushActionStat, event)
                details = EventConsolePage.viewEventDetails(user, pushActionStat, event)

                EventConsolePage.goToEventResource(user, pushActionStat, event)
                # NOTE - pushActionStat here is bound to the
                # "CloseEvents" workflow, which is what we want so that
                # stats are associated with this run of CloseEvents
                InvestigateCurrentDevice().run(user, pushActionStat)
                NavigationPage.goToEventConsole(user, pushActionStat)

                EventConsolePage.addLogMessageToEvent(user, pushActionStat, event)
                EventConsolePage.closeEvent(user, pushActionStat, event)
                user.think(1)
                return

        user.log("could not find any unacknowledged critical events");
        user.think(1)
