from selenium.webdriver.support.wait import WebDriverWait

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

def find(d, selector):
    return d.find_element_by_css_selector(selector)

def findMany(d, selector):
    return d.find_elements_by_css_selector(selector)

def findIn(el, selector):
    return el.find_element_by_css_selector(selector)

def wait(d, fn, time=10):
    WebDriverWait(d, time).until(fn)
