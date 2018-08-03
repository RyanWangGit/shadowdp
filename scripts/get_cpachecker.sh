#!/bin/sh

git clone https://github.com/sosy-lab/cpachecker.git
cd cpachecker
git checkout 5db731a28288ad013691d3f6e26d0af8d266342b
ant
cd ..
