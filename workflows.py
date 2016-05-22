import traceback
from common import *
import login_page as LoginPage
import devices_page as DevicesPage
import event_console_page as EventConsolePage
import navigation as Navigation

class Workflow(object):
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__
        self.args = kwargs

class LoginAndLogout(Workflow):
    @timed
    def run(self, user):
        workflowResult = WorkflowResult(self.name)

        baseURL = self.args["baseURL"]
        username = self.args["user"]
        password = self.args["password"]

        result = takeAction(
            workflowResult, LoginPage.login,
            user, baseURL, username, password)
        if not result.success:
            return workflowResult

        user.log("logged in (%is)" % result.stat["login.elapsedTime"])

        user.think(1)

        result = takeAction(workflowResult, Navigation.logout, user)
        if not result.success:
            return workflowResult

        user.log("logged out (%is)" % result.stat["logout.elapsedTime"])
        user.log("success")

        return workflowResult

class AckEvents(Workflow):
    @timed
    def run(self, driver):
        result = WorkflowResult(self.name)

        takeAction(result, Navigation.goToEventConsole, driver)
        if not result.success:
            return result

        takeAction(result, EventConsolePage.getEvents, driver)
        if not result.success:
            return result

        takeAction(result, EventConsolePage.ackAll, driver)
        if not result.success:
            return result

        return result

class CheckDevice(Workflow):
    def __init__(self, ip):
        Workflow.__init__(self)
        self.ip = ip

    @timed
    def run(self, driver):
        result = WorkflowResult(self.name)

        takeAction(result, Navigation.goToDevicesPage, driver)
        if not result.success:
            return result

        takeAction(result, DevicesPage.filterByIp, driver, self.ip)
        if not result.success:
            return result

        takeAction(result, DevicesPage.goToDeviceDetailPage, driver, self.ip)

        return result

def takeAction(result, action, *actionArgs):
    actionResult = action(*actionArgs)
    result.addActionResult(actionResult)
    return actionResult
