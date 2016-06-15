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

        # stare at the screen REAL hard
        user.think(8)

        # TODO - refresh/filter/sort
