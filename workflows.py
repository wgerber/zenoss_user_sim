from common import *
import login_page as LoginPage
import devices_page as DevicesPage
import event_console_page as EventConsolePage
import navigation as Navigation

# Move this to sim driver
ZENOSS_URL = 'https://zenoss5.zenoss-1310-d'
ZENOSS_USERNAME = 'Young'
ZENOSS_PASSWORD = 'Zenoss1234'

class Workflow(object):
    def __init__(self):
        self.driver = None
        self.name = self.__class__.__name__

class Login(Workflow):
    @timed
    def run(self, driver):
        result = WorkflowResult(self.name)

        takeAction(
            result, LoginPage.login,
            driver, ZENOSS_URL, ZENOSS_USERNAME, ZENOSS_PASSWORD)

        return result

class AckEvents(Workflow):
    def run(self, driver):
        result = WorkflowResult(self.name)
        start = time.time()

        takeAction(result, Navigation.goToEventConsole, driver)
        if not result.success:
            return result

        takeAction(result, EventConsolePage.getEvents, driver)
        if not result.success:
            return result

        takeAction(result, EventConsolePage.ackAll, driver)
        if not result.success:
            return result

        elapsedTime = time.time() - start
        result.putStat('elapsedTime', elapsedTime)

        return result

class CheckDevice(Workflow):
    def __init__(self, ip):
        Workflow.__init__(self)
        self.ip = ip

    def run(self, driver):
        start = time.time()

        Navigation.goToDevicesPage(driver)
        result = DevicesPage.filterByIp(driver, self.ip)
        print result

        end = time.time()
        stat = {'elapsedTime': end - start}

        return {'success': True, 'stat': stat}

def takeAction(result, action, *actionArgs):
    result.addActionResult(action(*actionArgs))
