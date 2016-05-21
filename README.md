# Zenoss User Simulator
This tool simulators user actions against the Zenoss UI. It also provides convenient ways to store and retrieve stats about the simulated user experience. 

### User
[TODO]

### Pages
Pages are a collection of functions called page actions. Page actions represent a task that a page can perform, eg: display a list of devices or acknowledge an event. It is important to note that page actions should be actions that make sense by themselves, outside of a web page. For example, a good action is "acknowledge event". A bad action is "click acknowledge button" as this leaks the implementation of the action (button clicks in a web page).

To enforce this separation of concerns, pages are also the only place the selenium, the web browser, and the DOM should exist and be addressed.

Page actions should throw errors in the case of unexpected failures, or catch errors and return failed Results.

### Workflow
A workflow is collection of actions that a user performs in order to accomplish a particular goal. For example, a user may want to catch up on what events were created overnight, so he may navigate to the event page, filter to show only critical events, then sort by last seen.

Workflows should be completely unaware of the underlying web browser implementation of the actions, and should solely be concerned with the actions themselves. Workflows should also be prepared to catch errors during any page actions, and handle them appropriatly. Workflows should only raise exceptions if things get real bad.A

A Workflow returns a WorkflowResult, which contains [TODO]
