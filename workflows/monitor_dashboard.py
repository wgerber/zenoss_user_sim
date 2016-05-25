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

def doMany(*args):
    for a in args:
        if not a[0](*a[1]):
            return False
    return True

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
