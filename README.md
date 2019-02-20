# ShadowDP

[![Build Status](https://travis-ci.com/RyanWangGit/shadowdp.svg?token=6D8zTzZr7SPui6PzhT2a&branch=master)](https://travis-ci.com/RyanWangGit/shadowdp) [![codecov](https://codecov.io/gh/RyanWangGit/shadowdp/branch/master/graph/badge.svg?token=ZrKPNQCjub)](https://codecov.io/gh/RyanWangGit/shadowdp)

A verification tool for differentially private algorithms based on a new proving technique "Shadow Execution".

## Getting Started
### Overview
As described in Section 6 of our paper, ShadowDP consists of two components: (1) a type system that type checks the algorithm and generate transformed program (with explicit privacy cost variable calculations and other assertions). (2) a verifier to verify the assertions in the transformed program always hold. We implemeneted the first component as a trans-compiler from C to C in Python. For the second component we use an off-the-shelf model checking tool [CPA-Checker](https://cpachecker.sosy-lab.org/).

### Using Docker

Using docker is the easiest way to set everything up and running.

```bash
docker pull cmlapsu/shadowdp
docker run --it cmlapsu/shadowdp bash
```

Then you'll be in a shell inside a docker container.

### Install Manually

If Docker isn't an available option for you, you can install ShadowDP manually following the steps below. Safely skip this section if you used docker.

**System Requirements**.
Python 3.5 / 3.6 / 3.7 on Linux is required, specifically we tested in Python 3.5 / 3.6 / 3.7 on Ubuntu 16.04 LTS. This is due to the requirements from the verification tool we use (i.e., [CPA-Checker](https://cpachecker.sosy-lab.org/)), which lacks many pre-compiled solver backends on other operating systems (e.g. MathSAT5 and z3 on macOS). 

In addition, `wget` package and JAVA 1.8 (exact version, CPA-Checker v1.7 won't work properly with JAVA 10 or 11) are required. Install them via
```bash
sudo apt-get update -y
sudo apt-get install python3 wget openjdk-8-jdk
```

**Download CPA-Checker.** 
As pre-compiled CPA-Checker binaries are relatively large, we don't include them as part of this artifact, you'll have to download them yourself. CPA-Checker v1.7 was used at the time of submission and it can be downloaded [here](https://cpachecker.sosy-lab.org/download-oldversions.php). Download the tarball, untar the file and rename the folder to `cpachecker`. Or run `scripts/get_cpachecker.sh` to take care of the download for you.

**Install ShadowDP.**
`venv` is highly recommended in order not to interfere with your system packages (or if you prefer Anaconda, conda environments setup is similar).

```bash
python3 -m venv venv
source venv/bin/acitvate
# now we're in virtual environment
python3 setup.py install
```

## Usage

For example, in order to verify `noisymax.c`, simply run `shadowdp noisymax.c`, and ShadowDP will type check and transform the source code, then invoke CPA-Checker to verify the transformed code. Argument `-c <dir> / --checker <dir>` can be used to specify the folder of pre-compiled CPA-Checker, by default it uses `./cpachecker` (You don't have to use it if followed the instructions).

All the case-studied algorithms are implemented in plain C in `examples/` folder with names `noisymax.c` / `svt.c` / `partiasum.c` / `smartsum.c` / `diffsvt.c`.

We also provide a script `scripts/benchmark.py` to verify all programs included in our paper at once, simply run `python ./scripts/benchmark.py ./examples` and the script will type check / transform / verify all provided examples in `examples/` folder.


## License
[MIT](https://github.com/RyanWangGit/shadowdp/blob/master/LICENSE).
