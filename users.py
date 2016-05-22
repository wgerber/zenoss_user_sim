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
    def __init__(self, name, url, username, password, skill=INTERMEDIATE, logDir=None, chromedriver=None):
        self.name = name
        self.url = url
        self.username = username
        self.password = password
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
        self.results = []
        self.hasQuit = False

    def work(self):
        self.log("beginning work")
        for workflow in self.workflows:
            self.log("beginning workflow %s" % workflow.name)
            result = workflow.run(self)
            self.results.append(result)
            if not result.success:
                print 'workflow {} failed, user {} quitting'.format(workflow.name, self.name)
                self.quit()
            else:
                self.log("workflow %s successful (%is)" % (workflow.name, result.stat[workflow.name + ".elapsedTime"]))
        totalTime = reduce(lambda acc,w: w.stat[w.name + ".elapsedTime"] + acc, self.results, 0)
        self.log("all workflows complete (%is)" % totalTime)

    def quit(self):
        if not self.hasQuit:
            self.hasQuit = True
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
