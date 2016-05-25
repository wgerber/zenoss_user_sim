from common import *
from pages import LoginPage, DashboardPage, NavigationPage

class MonitorDashboard(Workflow):
    @timed
    @screenshot
    def run(self, user):
        result = WorkflowResult(self.name)
        do = doer(result, user)

        if not user.loggedIn:
            result.fail("user is not logged in")
            return result

        workStart = time.time()
        if not do(NavigationPage.goToDashboard, (user,)):
            return result
        result.putStat('workTime', time.time() - workStart)

        # stare at the screen REAL hard
        user.think(8)

        # TODO - refresh

        return result
