from common import *
from pages import LoginPage, DashboardPage, NavigationPage

class MonitorDashboard(Workflow):
    def run(self, user, pushActionStat):
        if not user.loggedIn:
            raise WorkflowException(whoami(), "user is not logged in")

        NavigationPage.goToDashboard(user, pushActionStat);

        # stare at the screen REAL hard
        user.think(8)
