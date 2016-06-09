import time
from common import *
from pages import LoginPage, EventConsolePage, NavigationPage

class AckEvents(Workflow):
    def run(self, user, pushActionStat):
        if not user.loggedIn:
            raise WorkflowException(whoami(), "user is not logged in")

        NavigationPage.goToEventConsole(user, pushActionStat)
        EventConsolePage.filterBySeverity(user, pushActionStat, "critical")
        EventConsolePage.sortByLastSeen(user, pushActionStat, "ascending")

        # TODO - turn on event id column
        events = EventConsolePage.getEvents(user, pushActionStat)

        for e in events:
            if e["severity"] == "critical":
                print "oh snap, crit event %s!" % e["evid"]
                # TODO - investigate device
                # TODO - add log message
                # TODO - ack event
                user.think(2)
                return

