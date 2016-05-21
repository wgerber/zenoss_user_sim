from collections import defaultdict
from selenium import webdriver

from workflows import Workflow

class User(object):
    def __init__(self, name, chromedriver):
        self.name = name
        self.driver = webdriver.Chrome(chromedriver)
        # TODO - remove implicit wait eventually
        self.driver.implicitly_wait(10)
        self.workflows = []
        # TODO - stat and results can probably be the same thing
        self.stat = {}
        self.results = []

    def work(self):
        for workflow in self.workflows:
            result = workflow.run(self.driver)
            self.stat.update(result.stat)
            self.results.append(result)
            if not result.success:
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

    # TODO - log
    # TODO - screenshots
    # TODO - think
