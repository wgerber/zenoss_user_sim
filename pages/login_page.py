from common import *

TITLE = 'Login'

locator = {"loginField": "#username",
            "passField": "#passwrd",
            "submitBtn": "#loginButton"}

@assertPageAfter('title', 'Zenoss: Dashboard')
def login(user, pushActionStat, url, username, password):
    elapsed = StatRecorder(pushActionStat, whoami(), "elapsedTime");
    waitTimer = StatRecorder(pushActionStat, whoami(), "waitTime");
    elapsed.start()
    waitTimer.start()
    try:
        user.driver.get(url)
    except Exception as e:
        raise PageActionException(whoami(),
                "could not navigate to %s because %s" % (url, e.msg),
                screen=e.screen)
    waitTimer.push("_getUrl")

    try:
        login_field = find(user.driver, locator["loginField"])
        pass_field = find(user.driver, locator["passField"])
        submit_btn = find(user.driver, locator["submitBtn"])
    except Exception as e:
        raise PageActionException(whoami(),
                "unexpected failure logging in to %s: %s" % (url, e.msg),
                screen=e.screen)
    waitTimer.push("_findElements")

    try:
        login_field.send_keys(username)
        user.think(1)
        pass_field.send_keys(password)
        user.think(1)
        # after click, the dashboard page is loaded,
        # so this may take a bit of time
        submit_btn.click()
    except Exception as e:
        raise PageActionException(whoami(),
                "unexpected failure in logging in to %s: %s" % (url, e.msg),
                screen=e.screen)

    waitTimer.stop("_submitAndNavigate")
    elapsed.stop()
