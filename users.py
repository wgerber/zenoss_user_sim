from collections import defaultdict
from selenium import webdriver

from workflows import Workflow

# Feed this from top level
CHROMEDRIVER = '/home/ylee/Downloads/chromedriver'

class User(object):
    def __init__(self):
        self.driver = webdriver.Chrome(CHROMEDRIVER)
        self.driver.implicitly_wait(10)
        self.workflows = []
        self.stat = defaultdict(list)

    def work(self):
        for workflow in self.workflows:
            result = workflow.run(self.driver)
            if result['success']:
                self.stat[workflow.name].append(result['stat'])
            else:
                print 'User quits while doing {}'.format(workflow.name)
                self.quit()

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

