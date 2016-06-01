import traceback
from common import *
from pages import LoginPage, NavigationPage

class Login(Workflow):
    def run(self, user, pushActionStat):
        LoginPage.login(user, pushActionStat, user.url, user.username, user.password)
        user.loggedIn = True
        user.think(1)

class Logout(Workflow):
    def run(self, user, pushActionStat):
        if not user.loggedIn:
            raise WorkflowException(whoami(), "user is not logged in")
        NavigationPage.logout(user, pushActionStat)
        user.loggedIn = False
