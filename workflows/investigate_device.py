import time
from common import *
from pages import DeviceDetailsPage

class InvestigateDevice(Workflow):
    @timed
    @screenshot
    def run(self, user):
        result = WorkflowResult(self.name)
        do = doer(result, user)

        if not user.loggedIn:
            result.fail("user is not logged in")
            return result

        # TODO - figure out how to get the device in here
        user.driver.get("https://zenoss5.graveyard.zenoss.loc/zport/dmd/Devices/Server/Linux/devices/237000a8d8/devicedetail#deviceDetailNav:device_overview")
        if not do(DeviceDetailsPage.viewDeviceGraphs, (user,)):
            return result

        user.think(3)

        if not do(DeviceDetailsPage.interactWithDeviceGraphs, (user,)):
            return result

        componentNames = DeviceDetailsPage.getComponentNames(user)

        import pprint; pprint.pprint(componentNames)

        if not do(DeviceDetailsPage.viewComponentDetails, (user, componentNames[0])):
            return result

        time.sleep(4)

        # TODO - view a few different components
        # TODO - perform device command

        """
        workStart = time.time()
        if not do(NavigationPage.goToDashboard, (user,)):
            return result
        result.putStat('workTime', time.time() - workStart)

"""
        # stare at the screen REAL hard
        user.think(8)

        # TODO - refresh

        return result

def doer(result, user):
    def fn(actionFn, args):
        # perform action
        actionResult = takeAction(result, actionFn, *args)
        # log success/fail message
        message = ""
        if result.success:
            message += "successfully performed"
        else:
            message += "failed to perform"
        message += " %s" % actionFn.__name__
        elapsed = actionResult.stat["%s.elapsedTime" % actionFn.__name__]
        if elapsed is not None:
            message += " (%is)" % elapsed
        user.log(message)
        return result.success
    return fn
