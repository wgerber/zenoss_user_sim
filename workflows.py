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
    def run(self, driver):
        workflowResult = WorkflowResult(self.name)
        start = time.time()

        result = LoginPage.login(
            driver, ZENOSS_URL, ZENOSS_USERNAME, ZENOSS_PASSWORD)
        workflowResult.putTaskResult(result)

        end = time.time()
        stat = {'elapsedTime': end - start}

        return workflowResult

class AckEvents(Workflow):
    def run(self, driver):
        workflowResult = WorkflowResult(self.__class__.__name__)
        start = time.time()

#        result = Navigation.goToEventConsole(driver)
#        workflowResult.merge(result)

        performTask(driver, Navigation.goToEventConsole, workflowResult)
        if not workflowResult.success:
            return workflowResult

        performTask(driver, EventConsolePage.getEvents, workflowResult)
        if not workflowResult.success:
            return workflowResult

        performTask(driver, EventConsolePage.ackAll, workflowResult)
        if not workflowResult.success:
            return workflowResult

        end = time.time()
        stat = {'elapsedTime': end - start}

        return workflowResult

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

def performTask(driver, task, workflowResult):
    result = task(driver)
    workflowResult.putTaskResult(result)
