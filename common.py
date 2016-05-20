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

class assertPageAfter(object):
    def __init__(self, title):
        self.title = title

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            assert self.title in args[0].title, \
                '{}() is called on the wrong page, {}.'.format(
                    f.__name__, self.title)
            return result
        return wrapper

def find(d, selector):
    return d.find_element_by_css_selector(selector)

def findMany(d, selector):
    return d.find_elements_by_css_selector(selector)

def findIn(el, selector):
    return el.find_element_by_css_selector(selector)


