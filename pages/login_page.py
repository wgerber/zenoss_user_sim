import traceback
from common import *

TITLE = 'Login'

locator = {"loginField": "#username",
            "passField": "#passwrd",
            "submitBtn": "#loginButton"}

@timed
@assertPageAfter('title', 'Zenoss: Dashboard')
@screenshot
def login(user, url, username, password):
    result = ActionResult('login')

    try:
        user.driver.get(url)
    except:
        # TODO - get details from exception
        result.fail("could not navigate to %s" % url)
        traceback.print_exc()
        return result

    try:
        login_field = find(user.driver, locator["loginField"])
        pass_field = find(user.driver, locator["passField"])
        submit_btn = find(user.driver, locator["submitBtn"])
    except:
        # TODO - get details from exception
        result.fail("unexpected failure in login")
        traceback.print_exc()
        return result

    try:
        login_field.send_keys(username)
        user.think(1)
        pass_field.send_keys(password)
        user.think(1)
        submit_btn.click()
    except:
        # TODO - get details from exception
        result.fail("unexpected failure in login")
        traceback.print_exc()
        return result

    return result
