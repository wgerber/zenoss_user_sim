from workflows import Workflow, takeAction
from common import *
import login_page as LoginPage
import event_console_page as EventConsolePage
import navigation as NavigationPage

class WhatHappenedLastNight(Workflow):
    @timed
    @screenshot
    def run(self, user):
        result = WorkflowResult(self.name)
        do = doer(result, user)

        # login
        if not do(LoginPage.login, 1, (user, user.url, user.username, user.password)):
            return result

        # go to event console
        if not do(NavigationPage.goToEventConsole, 1, (user,)):
            return result

        # filter events to critical only
        if not do(EventConsolePage.filterBySeverity, 1, (user, "critical")):
            return result

        # sort events by last seen
        if not do(EventConsolePage.sortByLastSeen, 1, (user, "ascending")):
            return result

        return result

def doer(result, user):
    def fn(actionFn, duration, args):
        # perform action
        actionResult = takeAction(result, actionFn, *args)
        # wait/think for a moment
        user.think(duration)
        # log success/fail message
        if result.success:
            user.log("successfully performed '%s' (%is)" % (actionFn.__name__,
                actionResult.stat["%s.elapsedTime" % actionFn.__name__]))
            return True
        else:
            user.log("failed to perform '%s' (%is)" % (actionFn.__name__,
                actionResult.stat["%s.elapsedTime" % actionFn.__name__]))
            return False
    return fn
