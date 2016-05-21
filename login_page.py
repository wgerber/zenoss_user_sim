from common import *
import dashboard_page as DashboardPage

TITLE = 'Login'
locator = {'loginButton': (By.ID, 'loginButton'),
           'username': (By.NAME, '__ac_name'),
           'password': (By.NAME, '__ac_password')}

def timed(f):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        elapsedTime = time.time() - start
        result.putStat('elapsedTime', elapsedTime)
        return result
    return wrapper

@timed
@assertPageAfter('Zenoss: Dashboard')
def login(driver, url, username, password):
    driver.get(url)

    try:
        element = 'loginButton'
        timeout = 10
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator[element]))
    except TimeoutException:
        print "{} was not loaded in {} secs.".format(element, timeout)
        return False

    driver.find_element(*locator['username']).send_keys(username)
    driver.find_element(*locator['password']).send_keys(password)
    driver.find_element(*locator['loginButton']).click()

    result = ActionResult('login')

    return result

def logout(self):
    pass

