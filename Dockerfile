# MIT License
#
# Copyright (c) 2019 Yuxin (Ryan) Wang
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
FROM ubuntu:18.04

# install essential stuff
RUN apt-get update -y
RUN apt-get install -y --no-install-recommends gcc software-properties-common git ant

# install python
RUN apt-get install -y --no-install-recommends python3 python3-pip python3-setuptools

# install vim for debugging purposes
RUN apt-get install -y --no-install-recommends vim

# install openjdk11
RUN add-apt-repository ppa:openjdk-r/ppa
RUN apt-get update -y
RUN apt-get install -y --no-install-recommends openjdk-11-jdk

# copy ShadowDP into the image
COPY . /shadowdp
WORKDIR /shadowdp

# install CPA-Checker
RUN bash ./scripts/get_cpachecker.sh

# remove build tools
RUN apt-get remove -y openjdk-11-jdk git ant
RUN apt-get autoremove -y
RUN apt-get install -y --no-install-recommends openjdk-11-jre

# cleanup apt-get lists to make size smaller
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# update pip
RUN pip3 install --upgrade pip

# install packages
RUN python3 setup.py install

# test run
CMD python3 -m shadowdp
