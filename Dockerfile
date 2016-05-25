FROM ubuntu:xenial

WORKDIR "/root"
RUN apt update -qq
RUN apt install -y -q python python-pip unzip wget xvfb

# add chrome repo
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" | tee -a /etc/apt/sources.list

# add googles public key
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

#install chrome
RUN apt update -qq
RUN apt install -y -q google-chrome-stable

RUN pip install selenium xvfbwrapper

# download and install chromedriver
RUN wget -c https://chromedriver.storage.googleapis.com/2.21/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN cp ./chromedriver /usr/bin/
RUN rm chromedriver*

# user simulator
ADD *.py ./
ADD workflows ./workflows
ADD pages ./pages

# TODO - shell script entrypoint to catch signals
# and stop script before killing the container
ENTRYPOINT ["python", "-u", "sim.py"]
CMD ["--help"]

# NOTE
# mount this image with `-v /dev/shm:/dev/shm` and `--privileged`
# to workaround a chrome bug. eg:
# docker run --privileged -t \
#    -v $(pwd)/log:/root/log \
#    -v /dev/shm:/dev/shm \
#    -v /etc/hosts:/etc/hosts \
#    userrunner:v3 \
#    -u https://zenoss5.graveyard.zenoss.loc \
#    -n zenny \
#    -p **** \
#    -c 10 \
#    --log-dir ./log
