import time
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from utils import find, wait

TITLE = 'Login'
elements = {"logoutLink": "#sign-out-link"}

def logout(driver, baseURL):
    if(baseURL + "/zport/dmd" not in driver.current_url):
        raise Exception("Expected to be logged in, got " + driver.current_url)

    logout_link = find(driver, elements["logoutLink"])
    logout_link.click()

    wait(driver, EC.title_contains("Login"))

    return True
