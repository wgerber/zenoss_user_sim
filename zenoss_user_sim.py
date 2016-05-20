import time
from xvfbwrapper import Xvfb

from pages import *


headless = True
if headless:
    xvfb = Xvfb(width=1100, height=800)
    xvfb.start()

if __name__ == '__main__':
    bob = User()
    login = Login()
    ackEvents = AckEvents()
    bob.addWorkflow([login, ackEvents])
    bob.work()
    print bob.stat
