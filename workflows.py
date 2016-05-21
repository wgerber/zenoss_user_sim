import traceback
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
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__
        self.args = kwargs

class LoginAndLogout(Workflow):
    @timed
    def run(self, driver):
        workflowResult = WorkflowResult(self.name)

        baseURL = self.args["baseURL"]
        username = self.args["user"]
        password = self.args["password"]

        # TODO - move this to some common actions page?
        # TODO - this is essentially a page action and should
        # not appear up here at the workflow level. this is a 
        # bit messy because were creating the action result
        # here
        actionResult = ActionResult('navigateToZenoss')
        try:
            # navigate to base zenoss url / login page
            driver.get(baseURL)
        except:
            # why we failed this particular action
            actionResult.failResult("could not navigate to %s" % baseURL)
            # NOTE - adding a failed action result to a workflow will
            # fail the workflow and note which result caused the failure
            workflowResult.addActionResult(actionResult)
            # why we failed the entire workflow
            traceback.print_exc()

        print "navigated to base url"

        try:
            takeAction(
                workflowResult, LoginPage.login,
                driver, baseURL, username, password)
        except:
            workflowResult.failResult("unexpected failure in login") 
            traceback.print_exc()

        print "logged in"

        # TODO - user think

        try:
            takeAction(
                workflowResult, Navigation.logout, driver)
        except:
            workflowResult.failResult("unexpected failure in logout") 
            traceback.print_exc()

        print "logged out"

        return workflowResult

class AckEvents(Workflow):
    @timed
    def run(self, driver):
        result = WorkflowResult(self.name)

        takeAction(result, Navigation.goToEventConsole, driver)
        if not result.success:
            return result

        takeAction(result, EventConsolePage.getEvents, driver)
        if not result.success:
            return result

        takeAction(result, EventConsolePage.ackAll, driver)
        if not result.success:
            return result

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
    actionResult = action(*actionArgs)
    result.addActionResult(actionResult)
