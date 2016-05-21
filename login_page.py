from common import *

TITLE = 'Login'

locator = {"loginField": "#username",
            "passField": "#passwrd",
            "submitBtn": "#loginButton"}

@timed
@assertPageAfter('Zenoss: Dashboard')
def login(driver, url, username, password):

    # assumes already on the login page
    login_field = find(driver, locator["loginField"])
    pass_field = find(driver, locator["passField"])
    submit_btn = find(driver, locator["submitBtn"])

    login_field.send_keys("zenny")
    #u.think(1)
    pass_field.send_keys("Z3n0ss123")
    #u.think(1)
    submit_btn.click()

    result = ActionResult('login')

    return result