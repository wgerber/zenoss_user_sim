# Zenoss User Simulator
This tool simulators user actions against the Zenoss UI. It also provides convenient ways to store and retrieve stats about the simulated user experience. 

## Usage
You will need Xvfb, chromedriver and chrome installed as well as python and pip.

And, you should `pip install selenium xfvb-wrapper` to get the required deps.

Once that's in order, try `python sim.py` to kick things off.

[TODO - dockerfile, command line args]

## Tell me more!
This tool functions similarly to an automated test runner but attempts to behave more like a user than an automated test. It focuses on defining user workflows that don't know or care about how a thing is done, but just that the user wants to do that thing. A workflow performs work through page actions, which are functions that encapsulate the details of performing the action against a page in the UI. When a page action is performed, stats about that page action can be pushed up to the workflow, providing a way to track the UI and user's performance.

### User
[TODO]

### Pages
Pages are a collection of functions called page actions. Page actions represent a task that a page can perform, eg: display a list of devices or acknowledge an event. It is important to note that page actions should be actions that make sense by themselves, outside of a web page. For example, a good action is "acknowledge event". A bad action is "click acknowledge button" as this leaks the implementation of the action (button clicks in a web page).

To enforce this separation of concerns, pages are also the only place the selenium, the web browser, and the DOM should exist and be addressed.

Page actions should throw errors in the case of unexpected failures, or catch errors and return failed Results.

### Workflow
A workflow is collection of actions that a user performs in order to accomplish a particular goal. For example, a user may want to catch up on what events were created overnight, so he may navigate to the event page, filter to show only critical events, then sort by last seen.

Workflows should be completely unaware of the underlying web browser implementation of the actions, and should solely be concerned with the actions themselves. Workflows should also be prepared to catch errors during any page actions, and handle them appropriatly. Workflows should only raise exceptions if things get real bad.A

A Workflow returns a WorkflowResult, which contains a list of page action results and stats. The stats can be arbitrarily defined.
