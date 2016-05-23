# Zenoss User Simulator
This tool simulators user actions against the Zenoss UI. It also provides convenient ways to store and retrieve stats about the simulated user experience.

## Usage
A Dockerfile is included that will build an image which can point simulated users at a Zenoss instance. First build the Dockerfile

    docker build -t zenoss/usersim:v1 .

Once the build is complete, the image can be launched and command line arguments passed in

    docker run --privileged -t \
        -v $(pwd)/log:/root/log \
        -v /dev/shm:/dev/shm \
        -v /etc/hosts:/etc/hosts \
        zenoss/usersim:v1 \
        -u https://zenoss5.graveyard.zenoss.loc \
        -n zenny \
        -p ****** \
        -c 10 \
        --log-dir ./log

Note that this image must be run as `privileged` and `/dev/shm` must be bindmounted for chrome to work properly. Mounting `/etc/hosts` into the image is useful because the Zenoss instance may only be reachable by hostname

To run directly in python, install dependencies (Xvfb and chromdriver for the OS, and selenium and xvfbwrapper for python), then kick it off with

    python sim.py \
        -u https://zenoss5.graveyard.zenoss.loc \
        -n zenny \
        -p ****** \
        -c 10 \
        --log-dir /tmp/

For configuration options, try `python sim.py --help` or `docker run zenoss/usersim:v1`.

## Tell me more!
Zenoss User Simulator is similar to a functional test runner, but aims to perform specific tasks and workflows at a more general level rather than verify that specific details behave in an expected way. A **User** is given a list of **Workflows** to perform. Each Workflow interacts with one or more **Pages**. Pages know precisely how to accomplish a task, and return **Results** indicating, among other details, if the task was successful or not.

For example, a user workflow may be to review all critical events that occurred overnight. The workflow tasks could be: view events, filter to show only critical severity, sort by last seen, look at results.

Viewing the events is a page action that breaks down to navigating to the events page. This is part of the NavigationPage (an unusual page in that it is always present). The workflow doesn't need to know the details of how to view events, just that it can tell the navigation page to take us there.

Once the page action has completed, a result is returned. The result encapsulates success, stats and an optional error message. It is up to the workflow to decide how to act if the result is not successful.

The next two steps are to filter and sort the events. These are page actions of the EventPage, so the workflow calls each and the page action returns results.

The final step is to look at the results. The EventPage can return a list of visible events, and the workflow can iterate through them and make choices about what to do with them. For instance, the current user might be named "Bob", and an event summary might say "BOB LOOK AT THIS RIGHT NOW". The workflow can choose then to view the details of the event. In the same way a user might take a few moments to gather info with their eyeballs, our user simulator can take a few moments to think. Intentional pauses like this makes the user more authentic in that more idle time occurs where the UI is still making requests to the backend and putting load on the server.

Note that the concept of the web browser is entirely encapsulated in page actions. No WebElements, selenium exceptions or other webby things should make it outside of Pages and page actions.

## Some Notes
**Pages**
* Inside of pages, use the `find`, `findMany`, `wait` and similar helper functions instead of directly calling selenium methods. Maintaining page actions when the framework changes will be much simpler.
* Write page actions in a way that does not indicate that they do browser-y stuff. Bad page action: `clickAcknowledgeButton`. Good page action `acknowledgeEvent`.
* A page action should not return until it is sure the page is ready. Find some DOM element or something to look for to ensure the page is actually ready and not merely loaded
