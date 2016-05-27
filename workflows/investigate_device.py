import time
from common import *
from pages import DeviceDetailsPage

class InvestigateDevice(Workflow):
    @timed
    @screenshot
    def run(self, user, pushActionStat):
        result = WorkflowResult(self.name)
        do = doer(result, user)

        if not user.loggedIn:
            result.fail("user is not logged in")
            return result

        # TODO - figure out how to get the device in here
        # TODO - time this
        user.driver.get(user.url + "/zport/dmd/Devices/Server/Linux/devices/237000a8d8/devicedetail#deviceDetailNav:device_overview")
        if not do(DeviceDetailsPage.viewDeviceGraphs, (pushActionStat,)):
            return result

        user.think(3)

        if not do(DeviceDetailsPage.interactWithDeviceGraphs, (pushActionStat,)):
            return result

        componentNames = DeviceDetailsPage.getComponentNames(user)

        for name in componentNames:
            if not do(DeviceDetailsPage.viewComponentDetails, (pushActionStat, name)):
                return result

        # TODO - perform device command

        # stare at the screen REAL hard
        user.think(8)

        return result
