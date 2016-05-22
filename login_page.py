from common import *

TITLE = 'Login'

locator = {"loginField": "#username",
            "passField": "#passwrd",
            "submitBtn": "#loginButton"}

@timed
@assertPageAfter('Zenoss: Dashboard')
def login(user, url, username, password):
    result = ActionResult('login')

    try:
        user.driver.get(url)
    except:
        screen = user.screenshot("navigate_to_login")
        # TODO - get details from exception
        result.fail("could not navigate to %s. saved screenshot %s" % (url, screen))
        traceback.print_exc()
        return result

    try:
        login_field = find(user.driver, locator["loginField"])
        pass_field = find(user.driver, locator["passField"])
        submit_btn = find(user.driver, locator["submitBtn"])
    except:
        screen = user.screenshot("login")
        # TODO - get details from exception
        result.fail("unexpected failure in login. screenshot saved as %s" % screen) 
        traceback.print_exc()
        return result

    try:
        login_field.send_keys(username)
        user.think(1)
        pass_field.send_keys(password)
        user.think(1)
        submit_btn.click()
    except:
        screen = user.screenshot("login")
        # TODO - get details from exception
        result.fail("unexpected failure in login. screenshot saved as %s" % screen) 
        traceback.print_exc()
        return result

    return result
