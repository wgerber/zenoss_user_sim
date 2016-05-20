import time, traceback

from pages import login_page as LoginPage
from pages import global_page as GlobalPage

class Workflow(object):
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__
        self.args = kwargs

class LoginAndOut(Workflow):
    def run(self, driver):
        start = time.time()

        baseURL = self.args["baseURL"]
        username = self.args["user"]
        password = self.args["password"]

        try:
            # navigate to base zenoss url / login page
            driver.get(baseURL)
        except:
            traceback.print_exc()
            return {'success': False, 'stat': {}, 'error': 'unable to navigate to %s' % baseURL}

        try:
            LoginPage.login(
                driver, baseURL, username, password)
        except:
            traceback.print_exc()
            return {'success': False, 'stat': {}, 'error': 'failed to log in'}

        try:
            GlobalPage.logout(
                driver, baseURL)
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

