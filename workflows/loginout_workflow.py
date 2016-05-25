import traceback
from common import *
from pages import LoginPage, NavigationPage

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

        takeAction(result, NavigationPage.logout, user)
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

        takeAction(result, NavigationPage.logout, user)
        if not result.success:
            return result

        user.log("logged out (%is)" % result.stat[self.name + ".logout.elapsedTime"])

        return result

