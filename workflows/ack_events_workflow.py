import traceback
from common import *
import login_page as LoginPage
import devices_page as DevicesPage
import event_console_page as EventConsolePage
import navigation_page as Navigation
import device_detail_page as DeviceDetailPage

class AckEvents(Workflow):
    @timed
    def run(self, user):
        result = WorkflowResult(self.name)

        if not user.loggedIn:
            result.fail("user is not logged in")
            return result

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

