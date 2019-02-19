# ShadowDP

[![Build Status](https://travis-ci.com/RyanWangGit/shadowdp.svg?token=6D8zTzZr7SPui6PzhT2a&branch=master)](https://travis-ci.com/RyanWangGit/shadowdp) [![codecov](https://codecov.io/gh/RyanWangGit/shadowdp/branch/master/graph/badge.svg?token=ZrKPNQCjub)](https://codecov.io/gh/RyanWangGit/shadowdp)

A verification tool for differentially private algorithms based on a new proving technique "Shadow Execution".

## Getting Started
### Overview
As described in `Section 6 Implementation` of our paper, ShadowDP consists of two components: (1) a type system that type checks the algorithm and generate transformed program (with explicit privacy cost variable calculations and other assertions). (2) a verifier to verify the assertions in the transformed program always hold. We implemeneted the first component as a trans-compiler from C to C in Python. For the second component we use an off-the-shelf model checking tool [CPA-Checker](https://cpachecker.sosy-lab.org/).

### System Requirements
Python 3.5 / 3.6 / 3.7 on Linux is required, specifically we tested in Python 3.5 / 3.6 / 3.6 on Ubuntu 16.04 LTS. This is due to the requirements from the verification tool we use (i.e., [CPA-Checker](https://cpachecker.sosy-lab.org/)), which lacks many pre-compiled solver backends on other operating systems (e.g. MathSAT5 and z3 on macOS).

### Download CPA-Checker 
As pre-compiled CPA-Checker binaries are relatively large, we don't include them as part of this artifact, you'll have to download them yourself. CPA-Checker v1.7 was used at the time of submission and it can be downloaded [here](https://cpachecker.sosy-lab.org/download-oldversions.php. Download the tarball, untar the file and rename the folder to `cpachecker`. Or run `scripts/get_cpachecker.sh` to take care of the download for you.

## Usage

`virtualenv` is highly recommended in order not to interfere with your system packages.

For example, in order to verify `noisymax.c`, simply run `python -m shadowdp noisymax.c`, and ShadowDP will type check and transform the source code, then invoke CPA-Checker to verify the transformed code. Argument `--cpachecker <dir>` can be used to specify the folder of pre-compiled CPA-Checker, by default it uses `./cpachecker` (You don't have to use it if followed the instructions).

All the case-studied algorithms are implemented in plain C in `examples/` folder

We also provide a script `scripts/benchmark.py` to verify all programs included in our paper at once, simply run `python ./scripts/benchmark.py ./examples` and the script will type check / transform / verify all provided examples in `examples/` folder.


## License
[MIT](https://github.com/RyanWangGit/shadowdp/blob/master/LICENSE).
