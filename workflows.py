import time, traceback

from pages import login_page as LoginPage
from pages import global_page as GlobalPage

# Move this to sim driver
ZENOSS_URL = 'https://zenoss5.graveyard.zenoss.loc'
ZENOSS_USERNAME = 'zenny'
ZENOSS_PASSWORD = 'Z3n0ss123'

class Workflow(object):
    def __init__(self):
        self.driver = None
        self.name = self.__class__.__name__

class LoginAndOut(Workflow):
    def run(self, driver):
        start = time.time()

        # navigate to base zenoss url / login page
        driver.get(ZENOSS_URL)

        try:
            LoginPage.login(
                driver, ZENOSS_URL, ZENOSS_USERNAME, ZENOSS_PASSWORD)
        except:
            traceback.print_exc()
            return {'success': False, 'stat': {}, 'error': 'failed to log in'}

        try:
            GlobalPage.logout(
                driver, ZENOSS_URL)
        except:
            traceback.print_exc()
            return {'success': False, 'stat': {}, 'error': 'failed to log out'}

        end = time.time()
        stat = {'elapsedTime': end - start}

        return {'success': True, 'stat': stat, 'error': None}

class AckEvents(Workflow):
    def run(self, driver):
        start = time.time()
        failResult = {'success': False, 'stat': None, 'error': 'failed at life'}

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

