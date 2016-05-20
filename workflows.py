from common import *
import login_page as LoginPage
import devices_page as DevicesPage
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
        start = time.time()

        LoginPage.login(
            driver, ZENOSS_URL, ZENOSS_USERNAME, ZENOSS_PASSWORD)

        end = time.time()
        stat = {'elapsedTime': end - start}

        return {'success': True, 'stat': stat}

class AckEvents(Workflow):
    def run(self, driver):
        start = time.time()
        failResult = {'success': False, 'stat': None}

# TODO: Return stat so far if fails
        result = DashboardPage.goToEventConsole(driver)

        if not result['success']:
            return failResult
#        if not EventConsolePage.filterBySeverity(driver, 'test'):
#            return {'success': False, 'stat': None}
        result = EventConsolePage.getEvents(driver)
        if not result['success']:
            return failResult
        print result

        if not EventConsolePage.ackAll(driver):
            return failResult

        end = time.time()
        stat = {'elapsedTime': end - start}

        return {'success': True, 'stat': stat}

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
