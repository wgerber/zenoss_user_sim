import time
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from common import assertPage

TITLE = 'Zenoss: Dashboard'
locator = {'header': '#header',
           'eventsNavBtn': '#Events-nav-button'}

@assertPage(TITLE)
def goToEventConsole(driver):
    time.sleep(3) # Wait until the pop-up disappears.
    driver.find_element_by_css_selector(locator['eventsNavBtn']).click()

    return {'success': True, 'data': None}

    # wait until the page is loaded.
    # check the page is actually event console.
    # If not, return false.

@assertPage(TITLE)
def checkPageLoaded(driver):
    try:
        element = 'header'
        timeout = 10
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, locator[element])))
    except TimeoutException:
        print "{} was not loaded in {} secs.".format(element, timeout)
        return False

    if TITLE in driver.title:
        return True
    else:
        return False
