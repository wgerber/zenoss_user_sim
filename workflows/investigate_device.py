import time, random
from common import *
from pages import DeviceDetailsPage

# TODO - pass in list of available devices, or
# better, pass in the URL to the device to investigate
deviceIds = [
    '014e24e944', '01b2a5a6e1', '0263dcf7dd', '029bbcd9f2', '02ac4daf88', '02ea8be723', '03515bb111', '035ca9e267', '03d51255e1', '0445c41993',
    '04ab4b123c', '04aeb20eb3', '04bd7c6f23', '057107a1cb', '05a7bb35b1', '05e4aab5ab', '05e5bd9366', '0637a09086', '06c5b2006f', '06d6a04b44',
    '0737c41da5', '0780a269c8', '07f4786595', '089c55595f', '08d820109b', '0918e6280b', '0a4ccfae1d', '0a8c7db464', '0aa7a563cd', '0ae0d9e904',
    '0c12b2d392', '0c4c3ea39e', '0c788959c9', '0dab93a03b', '0ddb055493', '0e044c71f9', '0f3ae314d4', '0f6963b91d', '0fa968edcc', '0fcaf100af',
    '0fd318864a', '10.171.100.93', '10.87.128.58']

class InvestigateDevice(Workflow):
    def run(self, user, pushActionStat):
        if not user.loggedIn:
            raise WorkflowException(whoami(), "user is not logged in")

        # TODO - time this
        user.driver.get("%s/zport/dmd/Devices/Server/Linux/devices/%s/devicedetail#deviceDetailNav:device_overview" % \
                                (user.url, random.choice(deviceIds)))

        DeviceDetailsPage.checkPageReady(user, pushActionStat)
        DeviceDetailsPage.viewDeviceGraphs(user, pushActionStat)
        user.think(3)
        DeviceDetailsPage.interactWithDeviceGraphs(user, pushActionStat)

        # TODO - contribute to wait?
        componentNames = DeviceDetailsPage.getComponentNames(user)
        for name in componentNames:
            DeviceDetailsPage.viewComponentDetails(user, pushActionStat, name)

        # TODO - perform device command

        # stare at the screen REAL hard
        user.think(8)
