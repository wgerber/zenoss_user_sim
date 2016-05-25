import traceback
from common import *
import login_page as LoginPage
import devices_page as DevicesPage
import event_console_page as EventConsolePage
import navigation_page as Navigation
import device_detail_page as DeviceDetailPage

class CheckDevice(Workflow):
    def __init__(self, ip):
        Workflow.__init__(self)
        self.ip = ip

    @timed
    def run(self, user):
        result = WorkflowResult(self.name)

        if not user.loggedIn:
            result.fail("user is not logged in")
            return result

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
            if not result.success:
                return result

            takeAction(result, DeviceDetailPage.lookAtComponentGraphs, user)

        return result

