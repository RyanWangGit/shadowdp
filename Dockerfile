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
# use clean image to install shadowdp
FROM openjdk:11-jre-slim 

COPY . /shadowdp
WORKDIR /shadowdp 

# install shadowdp
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    gcc \
    wget \
    unzip \
    libgomp1 \
    curl && \
    # and tini
    TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir .

RUN bash scripts/get_cpachecker.sh

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["/bin/bash"]
