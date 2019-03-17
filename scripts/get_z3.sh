# MIT License
#
# Copyright (c) 2018-2019 Yuxin (Ryan) Wang
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
#!/bin/sh
Z3_VERSION="4.8.4"
COMMIT="d6df51951f4c"

# TODO: add auto detection for more linux distributions
if [[ "$OSTYPE" == "linux-gnu" ]]; then
    OS_VERSION="ubuntu-14.04";
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS_VERSION="osx-10.14.1";
else
    echo "OS version not supported: $OSTYPE";
    exit 1;
fi

wget "https://github.com/Z3Prover/z3/releases/download/z3-$Z3_VERSION/z3-$Z3_VERSION.$COMMIT-x64-$OS_VERSION.zip" \
    -q --show-progress

rm -rf z3-${Z3_VERSION}.${COMMIT}-x64-${OS_VERSION}
unzip z3-${Z3_VERSION}.${COMMIT}-x64-${OS_VERSION}.zip
rm -rf z3
mkdir z3

# move python bindings to z3 folder
mv z3-${Z3_VERSION}.${COMMIT}-x64-${OS_VERSION}/bin/python/z3/* z3/
# move LICENSE file
mv z3-${Z3_VERSION}.${COMMIT}-x64-${OS_VERSION}/LICENSE.txt z3/
# move library file
if [[ "$OSTYPE" == "linux-gnu" ]]; then
    mv z3-${Z3_VERSION}.${COMMIT}-x64-${OS_VERSION}/bin/libz3.so z3/;
elif [[ "$OSTYPE" == "darwin"* ]]; then
    mv z3-${Z3_VERSION}.${COMMIT}-x64-${OS_VERSION}/bin/libz3.dylib z3/;
fi

# remove the rest of the files
rm z3-${Z3_VERSION}.${COMMIT}-x64-${OS_VERSION}.zip
rm -rf z3-${Z3_VERSION}.${COMMIT}-x64-${OS_VERSION}