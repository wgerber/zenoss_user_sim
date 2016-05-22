import time, os

from collections import defaultdict
from selenium import webdriver

from workflows import Workflow

# skill levels determine how long it takes
# for users to perform tasks
BEGINNER = 1.5
INTERMEDIATE = 1
ADVANCED = 0.5

class User(object):
    def __init__(self, name, skill=INTERMEDIATE, logDir=None, chromedriver=None):
        self.name = name
        self.skill = skill
        if logDir:
            self.logDir = "%s/%s" % (logDir, time.time())
            if not os.path.exists(self.logDir):
                os.makedirs(self.logDir)
            self.logFile = open(self.logDir + "/%s.log" % self.name, "w")
        if chromedriver:
            self.driver = webdriver.Chrome(chromedriver)
        else:
            self.driver = webdriver.Chrome()
        # TODO - remove implicit wait eventually
        self.driver.implicitly_wait(10)
        self.workflows = []
        # TODO - stat and results can probably be the same thing
        self.stat = {}
        self.results = []

    def work(self):
        for workflow in self.workflows:
            result = workflow.run(self)
            self.stat.update(result.stat)
            self.results.append(result)
            if not result.success:
                print 'User quits while doing {}'.format(workflow.name)
                self.quit()

    def quit(self):
        self.driver.quit()
        self.logFile.close()

    def addWorkflow(self, workflow):
        assert isinstance(workflow, list) or isinstance(workflow, Workflow),\
            'Invalid argument type'
        if type(workflow) is list:
            for w in workflow:
                self.addWorkflow(w)
        else:
            self.workflows.append(workflow)

    def think(self, duration):
        time.sleep(duration * self.skill)

    def log(self, message):
        logStr = "[%s] %s - %s\n" % (time.asctime(), self.name, message)
        self.logFile.write(logStr)
        print logStr[:-1]

    def screenshot(self, name):
        filename = self.logDir + "/%s-%s-screen.png" % (self.name, name)
        self.driver.save_screenshot(filename)
        return filename

    # TODO - screenshots
