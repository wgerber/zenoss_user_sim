import time, pprint
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
            assert self.title in args[0].driver.title, \
                '{}() is called on the wrong page, {}.'.format(
                    f.__name__, self.title)
            return f(*args, **kwargs)

        return wrapper

class assertPageAfter(object):
    def __init__(self, title):
        self.title = title

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            assert self.title in args[0].driver.title, \
                'Called {}() and expected page "{}", but found page "{}".'.format(
                    f.__name__, self.title, args[0].driver.title)
            return result
        return wrapper

def timed(f):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        if result.success:
            elapsedTime = time.time() - start
        else:
            elapsedTime = None
        result.putStat('elapsedTime', elapsedTime)
        return result
    return wrapper

def find(d, selector):
    return d.find_element_by_css_selector(selector)

def findMany(d, selector):
    return d.find_elements_by_css_selector(selector)

def findIn(el, selector):
    return el.find_element_by_css_selector(selector)

def merge(d1, d2):
    """Merge two dictionaries. The latter argument overwrites the former."""
    result = d1.copy()
    result.update(d2)
    return result

class Result(object):
    def __init__(self, name):
        self.name = name
        self.success = True
        self.stat = {}
        self.error = ""

    def __str__(self):
        return pprint.pformat(self.__dict__, indent=4)

    def putStat(self, k, v):
        k = '.'.join([self.name, k])
        self.stat[k] = v

    def fail(self, error):
        self.success = False
        self.error = error

class ActionResult(Result):
    def __init__(self, name):
        Result.__init__(self, name)
        self.data = {}

    def putData(self, k, v):
        k = '.'.join([self.name, k])
        self.data[k] = v

class WorkflowResult(Result):
    def __init__(self, name):
        Result.__init__(self, name)
        self.failedAction = None

    def addActionResult(self, result):
        if not result.success:
            self.failedAction = result.name
            # fail this workflow with the error
            # of the failing action result
            self.fail(result.error)
        self.success *= result.success
        for k, v in result.stat.iteritems():
            k = '.'.join([self.name, k])
            self.stat[k] = v
