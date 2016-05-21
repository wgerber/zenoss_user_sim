from common import *
import dashboard_page as DashboardPage

TITLE = 'Login'
locator = {'loginButton': (By.ID, 'loginButton'),
           'username': (By.NAME, '__ac_name'),
           'password': (By.NAME, '__ac_password')}

@assertPageAfter('Zenoss: Dashboard')
def login(driver, url, username, password):
    start = time.time()
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
    end = time.time()
    result = Result('login')
    result.putStat('elapsedTime', end - start)

    return result

def logout(self):
    pass

