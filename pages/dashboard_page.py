import time
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils import assertPage, find

TITLE = 'Zenoss: Dashboard'
locator = {'header': '#header',
           'eventsNavBtn': '#Events-nav-button'}

elements = {
        "welcomePortlet": "#app-portal .x-portal-column:nth-of-type(1) .x-portlet:nth-of-type(1)"
        }

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
        # wait till dashboard is loaded
        find(driver, elements["welcomePortlet"])
    except:
        # TODO - log failure reason
        return False

    return True
