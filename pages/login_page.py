import traceback
from common import *

TITLE = 'Login'

locator = {"loginField": "#username",
            "passField": "#passwrd",
            "submitBtn": "#loginButton"}

@assertPageAfter('title', 'Zenoss: Dashboard')
def login(user, pushActionStat, url, username, password):
    waitTime = 0

    actionStart = time.time()
    start = time.time()
    try:
        # TODO - enforce a timeout on this
        user.driver.get(url)
    except Exception as e:
        raise PageActionException(whoami(),
                "could not navigate to %s because %s" % (url, e.msg),
                screen=e.screen)
    waitTime += time.time() - start

    start = time.time()
    try:
        login_field = find(user.driver, locator["loginField"])
        pass_field = find(user.driver, locator["passField"])
        submit_btn = find(user.driver, locator["submitBtn"])
    except:
        raise PageActionException(whoami(), "unexpected failure in login" % url,
                screen=e.screen)
    waitTime += time.time() - start

    start = time.time()
    try:
        login_field.send_keys(username)
        user.think(1)
        pass_field.send_keys(password)
        user.think(1)
        submit_btn.click()
    except:
        raise PageActionException(whoami(), "unexpected failure in login" % url,
                screen=e.screen)
    waitTime += time.time() - start

    waitTime = time.time() - actionStart
    pushActionStat(whoami(), 'waitTime', waitTime, actionStart)
