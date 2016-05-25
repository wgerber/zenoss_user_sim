import time, os

from collections import defaultdict
from selenium import webdriver

from common import Workflow

# skill levels determine how long it takes
# for users to perform tasks
BEGINNER = 1.5
INTERMEDIATE = 1
ADVANCED = 0.5
GODLIKE = 0

class User(object):
    def __init__(self, name, url, username, password, skill=GODLIKE, logDir="", chromedriver=None, workHour=0):
        self.name = name
        self.url = url
        self.username = username
        self.password = password
        self.skill = skill
        self.logDir = logDir
        self.logFile = open(self.logDir + "/%s.log" % self.name, "w")
        if chromedriver:
            self.driver = webdriver.Chrome(chromedriver)
        else:
            self.driver = webdriver.Chrome()
        self.workflows = []
        self.results = []
        self.hasQuit = False
        self.loggedIn = False
        self.workHour = workHour

    def work(self):
        self.log("beginning work")
        login = self.workflows[0] # Assume the first workflow is always Login.
        logout = self.workflows[-1] # Assume the last workflow is always Logout.

        login.run(self)
        assert self.loggedIn, 'Login failed'
        start = time.time()
        HOUR_TO_SEC = 3600
        atWork = True

        while(atWork):
            for workflow in self.workflows[1:-1]:
                self.log("beginning workflow %s" % workflow.name)
                result = workflow.run(self)
                self.results.append(result)
                elapsedTime = result.stat[workflow.name + ".elapsedTime"]

                if not result.success:
                    self.log(
                        'workflow {} failed, user {} quitting'
                        .format(workflow.name, self.name))
                    self.quit()
                else:
                    self.log(
                        "workflow %s successful (%is)"
                        % (workflow.name, elapsedTime))

                hourSoFar = (time.time() - start)/HOUR_TO_SEC
                if hourSoFar > self.workHour:
                    atWork = False
                    break

        logout.run(self)
        assert not self.loggedIn, 'Logout failed'
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
        if self.hasQuit:
            print "cannot log to file, user has already quit"
        else:
            self.logFile.write(logStr)
            self.logFile.flush()
        print logStr[:-1]

    def screenshot(self, name):
        filename = self.logDir + "/%s-%s-screen.png" % (self.name, name)
        self.driver.save_screenshot(filename)
        return filename
