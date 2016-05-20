import time
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import dashboard_page as DashboardPage
from utils import find, wait, assertPage

TITLE = 'Login'
elements = {"loginField": "#username",
            "passField": "#passwrd",
            "submitBtn": "#loginButton"}

@assertPage(TITLE)
def login(driver, url, username, password):
    # assumes already on the login page
    login_field = find(driver, elements["loginField"])
    pass_field = find(driver, elements["passField"])
    submit_btn = find(driver, elements["submitBtn"])

    login_field.send_keys("zenny")
    #u.think(1)
    pass_field.send_keys("Z3n0ss123")
    #u.think(1)
    submit_btn.click()

    # wait till were on the right page
    wait(driver, lambda d: url + "/zport/dmd" in driver.current_url)

    DashboardPage.checkPageLoaded(driver)

    return True
