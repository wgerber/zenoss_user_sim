import traceback
from common import *
import login_page as LoginPage
import devices_page as DevicesPage
import event_console_page as EventConsolePage
import navigation_page as Navigation
import device_detail_page as DeviceDetailPage

class Login(Workflow):
    @timed
    def run(self, user):
        result = WorkflowResult(self.name)

        takeAction(
            result, LoginPage.login,
            user, user.url, user.username, user.password)
        if not result.success:
            return result
        user.log("logged in (%is)" % result.stat[self.name + ".login.elapsedTime"])

        user.loggedIn = True

        user.think(1)

        return result

class Logout(Workflow):
    @timed
    def run(self, user):
        result = WorkflowResult(self.name)

        if not user.loggedIn:
            result.fail("user is not logged in")
            return result

        takeAction(result, Navigation.logout, user)
        if not result.success:
            return result

        user.log("logged out (%is)" % result.stat[self.name + ".logout.elapsedTime"])

        user.loggedIn = False

        return result

class LoginAndLogout(Workflow):
    @timed
    def run(self, user):
        result = WorkflowResult(self.name)

        takeAction(
            result, LoginPage.login,
            user, user.url, user.username, user.password)
        if not result.success:
            return result
        user.log("logged in (%is)" % result.stat[self.name + ".login.elapsedTime"])

        user.think(1)

        takeAction(result, Navigation.logout, user)
        if not result.success:
            return result

        user.log("logged out (%is)" % result.stat[self.name + ".logout.elapsedTime"])

        return result

