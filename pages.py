import time
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class assertPage(object):
    def __init__(self, title):
        self.title = title

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            assert self.title in args[0].title, \
                '{}() is called on the wrong page, {}.'.format(
                    f.__name__, self.title)
            return f(*args, **kwargs)

        return wrapper

class LoginPage(object):
    """Assume that driver already proceeded to the login page."""

#    TITLE = 'Login'
    locator = {'loginButton': (By.ID, 'loginButton'),
               'username': (By.NAME, '__ac_name'),
               'password': (By.NAME, '__ac_password')}

    @staticmethod
    def login(driver, url, username, password):
        driver.get(url)

        try:
            element = 'loginButton'
            timeout = 10
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(LoginPage.locator[element]))
        except TimeoutException:
            print "{} was not loaded in {} secs.".format(element, timeout)
            return False

        driver.find_element(*LoginPage.locator['username']).send_keys(username)
        driver.find_element(*LoginPage.locator['password']).send_keys(password)
        driver.find_element(*LoginPage.locator['loginButton']).click()

        return DashboardPage.checkPageLoaded(driver)

    def logout(self):
        pass

class BasePageElement(object):
    """Base page class that is initialized on every page object class."""

    def __set__(self, obj, value):
        """Sets the text to the value supplied"""
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_name(self.locator))
        driver.find_element_by_name(self.locator).send_keys(value)

    def __get__(self, obj, owner):
        """Gets the text of the specified object"""
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_name(self.locator))
        element = driver.find_element_by_name(self.locator)
        return element.get_attribute("value")

class DashboardPage(object):
    TITLE = 'Zenoss: Dashboard'
    locator = {'header': '#header',
               'eventsNavBtn': '#Events-nav-button'}

    @staticmethod
    @assertPage(TITLE)
    def goToEventConsole(driver):
#         try:
#             timeout = 10
#             element = WebDriverWait(driver, timeout).until(
#                 EC.element_to_be_clickable(DashboardPage.locator['eventsButton']))
#         except TimeoutException:
#             print "The Events nav button didn't become clickable in {} secs.".format(timeout)
#             return False

        time.sleep(3) # Wait until the pop-up disappears.
        driver.find_element_by_css_selector(DashboardPage.locator['eventsNavBtn']).click()

        return {'success': True, 'data': None}

        # wait until the page is loaded.
        # check the page is actually event console.
        # If not, return false.

    @staticmethod
    @assertPage(TITLE)
    def checkPageLoaded(driver):
        try:
            element = 'header'
            timeout = 10
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, DashboardPage.locator[element])))
        except TimeoutException:
            print "{} was not loaded in {} secs.".format(element, timeout)
            return False

        if DashboardPage.TITLE in driver.title:
            return True
        else:
            return False

class EventConsolePage(object):
    # TODO: Differentiate EventConsole, EventArchive, etc.
    TITLE = 'Zenoss: Events'
    locator = {'severityBtn': (By.ID, 'events_grid-filter-severity-btnEl'),
               'selectBtn': (By.ID, 'select-button-btnEl'),
               'ackBtn': (By.ID, 'events_toolbar_ack-btnEl'),
               'refreshBtn': (By.NAME, 'refresh-button'),
               'allMenu': (By.ID, 'menuitem-1063-itemEl'),
               'events': '#events_grid-body table:nth-of-type(1) .x-grid-row',
               'eventStateElement': '.x-grid-cell-eventState',
               'eventState': {'new': '.status-icon-small-new'}}
    @staticmethod
    @assertPage(TITLE)
    def filterBySeverity(driver, severity):
# This doesn't work.
#         try:
#             timeout = 3
#             WebDriverWait(driver, timeout).until(
#                 EC.alert_is_present())
#         except TimeoutException:
#             print 'The alert did not disappear in {} secs'.format(timeout)
        time.sleep(3) # Wait until the pop-up disappears.

        try:
            element = 'severityBtn'
            timeout = 3
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(EventConsolePage.locator[element]))
        except TimeoutException:
            print '{} did not appear in {} secs'.format(element, timeout)

        driver.find_element(*EventConsolePage.locator['severityBtn']).click()

        return True

    @staticmethod
    @assertPage(TITLE)
    def selectAll(driver):
        time.sleep(3) # Wait until the pop-up disappears.

        try:
            element = 'selectBtn'
            timeout = 3
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(EventConsolePage.locator[element]))
        except TimeoutException:
            print '{} did not appear in {} secs'.format(element, timeout)
            return False

        driver.find_element(*EventConsolePage.locator['selectBtn']).click()
        driver.find_element(*EventConsolePage.locator['allMenu']).click()

        return True

    @staticmethod
    @assertPage(TITLE)
    def ackAll(driver):
        EventConsolePage.selectAll(driver)
        driver.find_element(*EventConsolePage.locator['ackBtn']).click()

        return True

    @staticmethod
    @assertPage(TITLE)
    def getEvents(driver):
        try:
            timeout = 10
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, EventConsolePage.locator['events'])))
        except TimeoutException:
            print "The Events nav button didn't become clickable in {} secs.".format(timeout)
            return False

        data = {'events': get_event_list(driver)}
        return {'success': True, 'data': data}

def get_event_list(d):
    # assumes at event page
    # wait for events grid to be ready
    find(d, "#events_grid")

    event_rows = findMany(d, "#events_grid-body table .x-grid-row")
    events = []
    for el in event_rows:
        events.append({
            "resource": findIn(el, ".x-grid-cell-device").text,
            "class": findIn(el, ".x-grid-cell-eventClass").text,
            "summary": findIn(el, ".x-grid-cell-summary").text,
            "first_seen": findIn(el, ".x-grid-cell-firstTime").text,
            "last_seen": findIn(el, ".x-grid-cell-lastTime").text,
            "count": findIn(el, ".x-grid-cell-count").text,
        })

    return events

def find(d, selector):
    return d.find_element_by_css_selector(selector)

def findMany(d, selector):
    return d.find_elements_by_css_selector(selector)

def findIn(el, selector):
    return el.find_element_by_css_selector(selector)
