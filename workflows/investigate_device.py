import time, random
from common import *
from pages import DeviceDetailsPage

# TODO - pass in list of available devices, or
# better, pass in the URL to the device to investigate
deviceIds = map(lambda i: "cisco2960G-40-%i" % i, range(20, 50))

devicePrefix = "cisco2960G-40-"

def doInvestigation(user, pushActionStat):
    DeviceDetailsPage.checkPageReady(user, pushActionStat)
    DeviceDetailsPage.viewDeviceGraphs(user, pushActionStat)
    user.think(3)
    DeviceDetailsPage.interactWithDeviceGraphs(user, pushActionStat)

    componentNames = DeviceDetailsPage.getComponentNames(user, pushActionStat)
    for name in componentNames:
        DeviceDetailsPage.viewComponentDetails(user, pushActionStat, name)

    # TODO - perform device command

class InvestigateDevice(Workflow):
    def run(self, user, pushActionStat):
        if not user.loggedIn:
            raise WorkflowException(whoami(), "user is not logged in")

        devId = random.choice(deviceIds)
        url = "%s/zport/dmd/Devices/Network/Cisco/10-160-40-x/devices/%s/devicedetail#deviceDetailNav:device_overview" % \
                (user.url, devId)

        # time the navigation action
        waitTimer = StatRecorder(pushActionStat, "navigateToDevice%s" % devId, "waitTime");
        waitTimer.start()
        user.driver.get(url)
        waitTimer.stop()

        doInvestigation(user, pushActionStat)

        # stare at the screen REAL hard
        user.think(8)

class InvestigateCurrentDevice(Workflow):
    def run(self, user, pushActionStat):
        if not user.loggedIn:
            raise WorkflowException(whoami(), "user is not logged in")

        doInvestigation(user, pushActionStat)

        # stare at the screen REAL hard
        user.think(8)
