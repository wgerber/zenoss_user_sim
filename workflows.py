import traceback
from common import *
import login_page as LoginPage
import devices_page as DevicesPage
import event_console_page as EventConsolePage
import navigation as Navigation
import device_detail_page as DeviceDetailPage

class Workflow(object):
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__

# since many workflows may need to login first,
# this provides a convenient way to do so
def login(user, result):
    # TODO - gracefully handle already logged in
    takeAction(
        result, LoginPage.login,
        user, user.url, user.username, user.password)
    return result

class LoginAndLogout(Workflow):
    @timed
    def run(self, user):
        result = WorkflowResult(self.name)

        login(user, result)
        if not result.success:
            return result
        user.log("logged in (%is)" % result.stat[self.name + ".login.elapsedTime"])

        user.think(1)

        takeAction(result, Navigation.logout, user)
        if not result.success:
            return result

        user.log("logged out (%is)" % result.stat[self.name + ".logout.elapsedTime"])

        return result

class AckEvents(Workflow):
    @timed
    def run(self, user):
        result = WorkflowResult(self.name)

        """
        login(user, result)
        if not result.success:
            return result
        user.log("logged in (%is)" % result.stat[self.name + ".login.elapsedTime"])
        """

        takeAction(result, Navigation.goToEventConsole, user)
        if not result.success:
            return result

        takeAction(result, EventConsolePage.getEvents, user)
        if not result.success:
            return result

        takeAction(result, EventConsolePage.ackAll, user)
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

        login(user, result)
        if not result.success:
            return result
        user.log("logged in (%is)" % result.stat[self.name + ".login.elapsedTime"])

        user.think(1)

        takeAction(result, Navigation.goToDevicesPage, user)
        if not result.success:
            return result

        user.think(1)

        actionResult = takeAction(result, DevicesPage.filterByIp, user, self.ip)
        if not result.success:
            return result

        if actionResult.data['filterByIp.devices']:
            takeAction(result, DevicesPage.goToDeviceDetailPage, user, self.ip)
            if not result.success:
                return result

            takeAction(result, DeviceDetailPage.getEvents, user, None, True)
            if not result.success:
                return result

            takeAction(result, DeviceDetailPage.lookAtGraphs, user)

        return result

# performs an action and automatically applies its
# results to the provided workflowResult
def takeAction(result, action, *actionArgs):
    actionResult = action(*actionArgs)
    result.addActionResult(actionResult)
    return actionResult
