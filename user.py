import time, os, sys
import json, traceback

from collections import defaultdict
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from common import *

# skill levels determine how long it takes
# for users to perform tasks
BEGINNER = 1.5
INTERMEDIATE = 1
ADVANCED = 0.5
GODLIKE = 0

REDDIT_TIME = 2

class User(object):
    def __init__(self, name, url, username, password, skill=INTERMEDIATE, logDir="", chromedriver=None, duration=0, tsdbQueue = None):
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
        self.duration = duration
        self.thinkTime = 0
        self.workflowsComplete = 0
        self.workflowsFailed = 0
        self.tsdbQueue = tsdbQueue

    # perform a workflow and handle any exceptions it may raise
    def executeWorkflow(self, workflow, pushActionStat):
        success = False
        try:
            workflow.run(self, pushActionStat)
            success = True
        except WorkflowException as e:
            self.log("workflow failed: %s %s" % (workflow.name, str(e)),
                    severity="ERROR")
            self.log(traceback.format_exc(sys.exc_info()[2]), severity="ERROR")
            self.workflowsFailed += 1
            # TODO - save e.screen
        except PageActionException as e:
            self.log("workflow failed: %s:%s %s" % (workflow.name, e.actionName, str(e)),
                    severity="ERROR")
            self.log(traceback.format_exc(sys.exc_info()[2]), severity="ERROR")
            self.workflowsFailed += 1
            # TODO - save e.screen
        except WebDriverException as e:
            self.log("workflow %s failed with uncaught WebDriverException: %s" % (workflow.name, str(e)),
                    severity="ERROR")
            self.log(traceback.format_exc(sys.exc_info()[2]), severity="ERROR")
            self.workflowsFailed += 1
            # TODO - save e.screen
        except KeyboardInterrupt:
            self.log("workflow %s failed due to KeyboardInterrupt" % workflow.name,
                    severity="ERROR")
            self.workflowsFailed += 1
            raise
        except Exception as e:
            self.log("workflow %s failed with uncaught error: %s" % (workflow.name, str(e)),
                    severity="ERROR")
            self.log(traceback.format_exc(sys.exc_info()[2]), severity="ERROR")
            self.workflowsFailed += 1
        return success

    def work(self):
        # TODO - handle log in/out here, dont include in workflow
        login = self.workflows[0] # Assume the first workflow is always Login.
        logout = self.workflows[-1] # Assume the last workflow is always Logout.

        pushActionStat = getPushActionStat(self.tsdbQueue, self.name, login.name)
        if not self.executeWorkflow(login, pushActionStat):
            # TODO - handle more gracefully
            self.log("could not log in", severity="ERROR")
            raise Exception("could not log in")

        start = time.time()
        HOUR_TO_SEC = 3600
        atWork = True

        while(atWork):
            for workflow in self.workflows[1:-1]:
		self.log("I've worked for %is of my total %is" % (time.time() - start, self.duration))
                self.log("beginning workflow %s" % workflow.name)
                pushActionStat = getPushActionStat(self.tsdbQueue, self.name, workflow.name)

                # perform workflow and handle exceptions
                # TODO - catch uncaught exceptions and gracefully
                # exit with the final "completed" report
                if self.executeWorkflow(workflow, pushActionStat):
                    self.log(
                        "workflow %s(#%i) successful"
                        % (workflow.name, self.workflowsComplete))

                    self.workflowsComplete += 1

                # take a reddit break
                time.sleep(REDDIT_TIME)

                # is it quittin time?
                if time.time() - start > self.duration:
                    self.log("It's quittin time after %is (%is total)" %(time.time() - start, self.duration),
			severity="DEBUG")
                    atWork = False
                    break

        pushActionStat = getPushActionStat(self.tsdbQueue, self.name, logout.name)
        if not self.executeWorkflow(logout, pushActionStat):
            # TODO - handle more gracefully
            self.log("could not log out", severity="ERROR")
            raise Exception("could not log out")

        self.log("completed %i workflows, failed %i workflows over %is" % (self.workflowsComplete, self.workflowsFailed, time.time() - start),
                severity="HAPPY")

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
        thinkTime = duration * self.skill
        time.sleep(thinkTime)
        self.thinkTime += thinkTime

    def log(self, message, toConsole=True, severity="INFO"):
        logStr = "[%s] %s %s - %s\n" % (time.asctime(), severity, self.name, message)
        if self.hasQuit:
            print "cannot log to file, user has already quit"
        else:
            self.logFile.write(logStr)
            self.logFile.flush()
        if toConsole:
            print colorizeString(logStr[:-1], severity)

    def screenshot(self, name):
        filename = self.logDir + "/%s-%s-screen.png" % (self.name, name)
        self.driver.save_screenshot(filename)
        return filename

    def postStat(self, stat):
        if self.tsdbQueue:
            data = []
            for k, v in stat.iteritems():
                data.append({'timestamp': time.time(), 'metric': k, 'value': v, 'tags': {'user': self.name}})
            self.tsdbQueue.put(data)

