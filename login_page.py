import time
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import dashboard_page as DashboardPage

TITLE = 'Login'
locator = {'loginButton': (By.ID, 'loginButton'),
           'username': (By.NAME, '__ac_name'),
           'password': (By.NAME, '__ac_password')}

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

    return DashboardPage.checkPageLoaded(driver)

def logout(self):
    pass

