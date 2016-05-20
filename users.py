import time
from collections import defaultdict
from selenium import webdriver

from workflows import Workflow

class User(object):
    def __init__(self, name="bob"):
        self.name = name
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.driver.set_window_size(1100, 800)
        self.workflows = []
        self.stat = defaultdict(list)

    def work(self):
        for workflow in self.workflows:
            print "beginning workflow %s" % workflow.name
            try:
                result = workflow.run(self.driver)
            except:
                print "something went really wrong"
                raise
            self.stat[workflow.name].append(result)
            if not result['success']:
                print 'User quit while doing {}'.format(workflow.name)
                self.quit()

    def think(self, duration):
        # TODO - multiply duration by self.skill_level
        time.sleep(duration)

    def quit(self):
        self.driver.quit()

    def addWorkflow(self, workflow):
        assert isinstance(workflow, list) or isinstance(workflow, Workflow),\
            'Invalid argument type'
        if type(workflow) is list:
            for w in workflow:
                self.addWorkflow(w)
        else:
            self.workflows.append(workflow)

