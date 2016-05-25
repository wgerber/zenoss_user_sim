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
    def __init__(self, name, url, username, password, skill=BEGINNER, logDir="", chromedriver=None):
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

    def work(self):
        self.log("beginning work")
        for workflow in self.workflows:
            self.log("beginning workflow %s" % workflow.name)
            result = workflow.run(self)
            self.results.append(result)
            if not result.success:
                print 'workflow {} failed, user {} quitting'.format(workflow.name, self.name)
                break
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
