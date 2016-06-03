import time
from common import *
from pages import NavigationPage, InfrastructurePage

class MonitorDevices(Workflow):
    def run(self, user, pushActionStat):
        if not user.loggedIn:
            raise WorkflowException(whoami(), "user is not logged in")

        NavigationPage.goToDevicesPage(user, pushActionStat)
        # TODO - look for critical devices
        # TODO - navigate to critical devices and inspect

        # stare at the screen REAL hard
        user.think(8)
