import time, pprint, inspect, socket
from functools import wraps

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# just some globals is all
DEFAULT_TIMEOUT = 60
MAX_RETRIES = 2

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
            if not self.expected in actual:
                raise PageActionException(whoami(),
                        '{}() is called on the wrong page, {}.'.format(f.__name__, self.expected))
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
            if not self.expected in actual:
                raise PageActionException(whoami(),
                        'Called {}() and expected page "{}", but found page "{}".'.format(f.__name__, self.expected, actual))
            return result
        return wrapper

class retry(object):
    def __init__(self, maxAttempts=1):
        self.maxAttempts = maxAttempts
	self.attempts = 0

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except (WorkflowException, PageActionException) as e:
                if self.attempts < self.maxAttempts:
                    print "retrying due to %s" % e.message
                    self.attempts += 1
                    return wrapper(*args, **kwargs)
                else:
                    print "gave up retrying"
                    raise
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

def ts():
    return time.time()

class Workflow(object):
    def __init__(self, **kwargs):
        self.name = self.__class__.__name__

def pushStat(queue, user, workflow, action, key, value, timestamp, simId):
    if queue:
        tags = {'host': socket.gethostname()}
        for k, v in zip(
                ['user', 'workflow', 'action', 'simId'],
                [user, workflow, action, simId]):
            if v:
                tags[k] = v

        data = [{'timestamp': timestamp, 'metric': key, 'value': value, 'tags': tags}]
        queue.put(data)

def getPushActionStat(queue, user, workflow, simId):
    def fn(action, key, value, timestamp):
        pushStat(queue, user, workflow, action, key, value, timestamp, simId)
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

class PageActionException(Exception):
    def __init__(self, actionName, message, screen=None):
        self.message = message
        self.screen = screen
        self.actionName = actionName

    def __str__(self):
        return "%s: %s" % (self.actionName, self.message)

class WorkflowException(Exception):
    def __init__(self, workflowName, message, actionName=None, screen=None):
        self.message = message
        self.screen = screen
        self.actionName = actionName
        self.workflowName = workflowName

    def __str__(self):
        if self.actionName:
            return "%s:%s %s" % (self.workflowName, self.actionName, self.message)
        else:
            return "%s: %s" % (self.workflowName, self.message)

class StopWatch(object):
    def __init__(self):
        self.times = []
        self.lastTime = None

    def start(self):
        self.lastTime = time.time()
        return self

    def stop(self):
        if not self.lastTime:
            return
        self.times.append(time.time() - self.lastTime)
        self.lastTime = None
        return self

    @property
    def total(self):
        curr = 0
        # if a timer is in progress, grab the
        # current value without stopping it
        if self.lastTime:
            curr = time.time() - self.lastTime
        return reduce(lambda x,y: x+y, self.times, curr)

class StatRecorder(object):
    def __init__(self, pushFn, name, metric):
        self.pushFn = pushFn
        self.name = name
        self.metric = metric
        self.startTime = None

    def start(self):
        self.startTime = time.time()

    def stop(self, suffix=""):
        """ stops AND pushes """
        if not self.startTime:
            return
        self._pushStat(self.startTime, time.time(), suffix=suffix)
        self.startTime = None

    def push(self, suffix=""):
        self._pushStat(self.startTime, time.time(), suffix=suffix)

    def _pushStat(self, start, end, suffix=""):
        total = end - start
        #self.pushFn(self.name + suffix, self.metric, total, start)
        self.pushFn(self.name + suffix, self.metric, total, end)
