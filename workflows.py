import traceback
from common import *
import login_page as LoginPage
import devices_page as DevicesPage
import event_console_page as EventConsolePage
import navigation as Navigation

class Workflow(object):
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__

class LoginAndLogout(Workflow):
    @timed
    def run(self, user):
        result = WorkflowResult(self.name)

        baseURL = user.url
        username = user.username
        password = user.password

        takeAction(
            result, LoginPage.login,
            user, baseURL, username, password)
        if not result.success:
            return result

        user.log("logged in (%is)" % result.stat["LoginAndLogout.login.elapsedTime"])

        user.think(1)

        takeAction(result, Navigation.logout, user)
        if not result.success:
            return result

        user.log("logged out (%is)" % result.stat["LoginAndLogout.logout.elapsedTime"])

        return result

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
    def run(self, user):
        result = WorkflowResult(self.name)

        baseURL = user.url
        username = user.username
        password = user.password

        takeAction(
            result, LoginPage.login,
            user, baseURL, username, password)
        if not result.success:
            return result

        user.log("logged in (%is)" % result.stat["CheckDevice.login.elapsedTime"])

        user.think(1)

        takeAction(result, Navigation.goToDevicesPage, user)
        if not result.success:
            return result

        user.think(1)

        takeAction(result, DevicesPage.filterByIp, user, self.ip)
        if not result.success:
            return result

        takeAction(result, DevicesPage.goToDeviceDetailPage, user, self.ip)

        return result

def takeAction(result, action, *actionArgs):
    actionResult = action(*actionArgs)
    result.addActionResult(actionResult)
    return actionResult
