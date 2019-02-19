# ShadowDP

[![Build Status](https://travis-ci.com/RyanWangGit/shadowdp.svg?token=6D8zTzZr7SPui6PzhT2a&branch=master)](https://travis-ci.com/RyanWangGit/shadowdp) [![codecov](https://codecov.io/gh/RyanWangGit/shadowdp/branch/master/graph/badge.svg?token=ZrKPNQCjub)](https://codecov.io/gh/RyanWangGit/shadowdp)

A verification tool for differentially private algorithms based on a new proving technique "Shadow Execution".

## Getting Started
### Overview
As described in Section 6 of our paper, ShadowDP consists of two components: (1) a type system that type checks the algorithm and generate transformed program (with explicit privacy cost variable calculations and other assertions). (2) a verifier to verify the assertions in the transformed program always hold. We implemeneted the first component as a trans-compiler from C to C in Python and tested under macOS / Windows / Linux. For the second component we use an off-the-shelf model checking tool [CPA-Checker](https://cpachecker.sosy-lab.org/).

### System Requirements
Linux, Ubuntu 16.04 LTS is recommended. This is due to the requirements from the verification tool we use (i.e., [CPA-Checker](https://cpachecker.sosy-lab.org/)), which lacks many solver backends on other operating systems (e.g. MathSAT5 and z3 on macOS).

### Download CPA-Checker 


## Guide
All the case-studied algorithms are implemented in plain C in `examples/` folder, 


## License
[MIT](https://github.com/RyanWangGit/Lang/blob/master/LICENSE).
