import time, pprint, inspect
from functools import wraps

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

DEFAULT_TIMEOUT = 120

class assertPage(object):
    def __init__(self, attr, expected):
        self.attr = attr
        self.expected = expected

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if self.attr == 'title':
                actual = args[0].driver.title
            elif self.attr == 'url':
                actual = args[0].driver.current_url
            assert self.expected in actual, \
                '{}() is called on the wrong page, {}.'.format(
                    f.__name__, self.expected)
            return f(*args, **kwargs)

        return wrapper

class assertPageAfter(object):
    def __init__(self, attr, expected):
        self.attr = attr
        self.expected = expected

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            if self.attr == 'title':
                actual = args[0].driver.title
            elif self.attr == 'url':
                actual = args[0].driver.current_url
            assert self.expected in actual, \
                'Called {}() and expected page "{}", but found page "{}".'.format(
                    f.__name__, self.expected, actual)
            return result
        return wrapper

def timed(f):
    @wraps(f)
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

def screenshot(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # NOTE - assumes user is first or second arg
        user = None
        if hasattr(args[0], "screenshot"):
            user = args[0]
        elif hasattr(args[1], "screenshot"):
            user = args[1]
        try:
            result = f(*args, **kwargs)
        except:
            if user:
                screen = user.screenshot(f.__name__)
                user.log("screenshot saved as %s" % screen)
            raise
        if not result.success:
            if user:
                screen = user.screenshot(f.__name__)
                user.log("screenshot saved as %s" % screen)
        return result
    return wrapper

class retry(object):
    def __init__(self, maxAttempts=1):
        self.maxAttempts = maxAttempts
	self.attempts = 0

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            while not result.success and self.attempts < self.maxAttempts:
                print "retrying"
                self.attempts += 1
                result = f(*args, **kwargs)
            if self.attempts >= self.maxAttempts:
                print "gave up retrying"
            return result
        return wrapper

def find(d, selector, timeout = DEFAULT_TIMEOUT):
    # NOTE - returns invisible elements as well
    return wait(d, EC.presence_of_element_located((By.CSS_SELECTOR, selector)), timeout)

def findMany(d, selector):
    # NOTE - returns invisible elements as well
    return wait(d, EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)), DEFAULT_TIMEOUT)

def findIn(el, selector):
    return el.find_element_by_css_selector(selector)

def findManyIn(el, selector):
    return el.find_elements_by_css_selector(selector)

def wait(d, fn, time=DEFAULT_TIMEOUT):
    return WebDriverWait(d, time).until(fn)

# get name of current function
def whoami():
    return inspect.stack()[1][3]

class Workflow(object):
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__

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

# performs an action and automatically applies its
# results to the provided workflowResult
def takeAction(result, action, *actionArgs):
    actionResult = action(*actionArgs)
    result.addActionResult(actionResult)
    return actionResult

def doer(result, user):
    def fn(actionFn, args):
        # perform action
        severity = "INFO"
        actionResult = takeAction(result, actionFn, *args)

        actionResultStr = "succesfully performed" if actionResult.success else "failed to perform"
        actionName = actionFn.__name__
        elapsedTime = actionResult.stat.get("%s.elapsedTime" % actionFn.__name__, None)
        elapsed = "(total %is)" % elapsedTime if elapsedTime is not None else ""
        waitTime = actionResult.stat.get("%s.waitTime" % actionFn.__name__, None)
        work = "(work %is)" % waitTime if waitTime is not None else ""
        message = "%s %s %s %s" % (actionResultStr, actionName, elapsed, work)
        if not actionResult.success:
            severity = "ERROR"
            if actionResult.error:
                message += "error: '%s'" % actionResult.error
        user.log(message, severity=severity)

        # put action result waitTime on workflow result
        if not "%s.waitTime" % result.name in result.stat:
            result.stat["%s.waitTime" % result.name] = 0
        result.stat["%s.waitTime" % result.name] += waitTime or 0

        return actionResult.success
    return fn

def colorizeString(s, severity):
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[1;%dm"
    BOLD_SEQ = "\033[1m"
    COLORS = {
        'WARN': YELLOW,
        'INFO': WHITE,
        'DEBUG': BLUE,
        'ERROR': RED,
        'HAPPY': GREEN
    }

    if severity == "INFO":
        return s
    else:
        return COLOR_SEQ % (30 + COLORS[severity]) + s + RESET_SEQ
