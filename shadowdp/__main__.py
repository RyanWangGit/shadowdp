# MIT License
#
# Copyright (c) 2018 Ryan Wang
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
import argparse
import coloredlogs
import os.path
import sys
import time
import logging
from pycparser import parse_file
from pycparser.c_generator import CGenerator
from shadowdp.core import LangTransformer
from shadowdp.checker import check


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', fmt='%(levelname)s:%(module)s: %(message)s')

__HEADER = r"""extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern int __VERIFIER_nondet_int();
extern void __VERIFIER_assume(int);
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }
#define abs(x) ((x) < 0 ? -(x) : (x))
typedef enum { false = 0, true = 1 } bool;
    
"""

__FUNCTION_MAP = {
    'assert': '__VERIFIER_assert',
    'assume': '__VERIFIER_assume',
    'havoc': '__VERIFIER_nondet_float'
}


def main(argv=sys.argv[1:]):
    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('file', metavar='FILE', type=str, nargs=1)
    arg_parser.add_argument('-o', '--out',
                            action='store', dest='out', type=str,
                            help='The output file name.', required=False)
    arg_parser.add_argument('-c', '--checker',
                            action='store', dest='checker', type=str, default='./cpachecker',
                            help='The checker path.', required=False)
    arg_parser.add_argument('-f', '--function',
                            action='store', dest='function', type=str, default=None,
                            help='The function to verify.', required=False)
    arg_parser.add_argument('-e', '--epsilon',
                            action='store', dest='epsilon', type=str, default=None,
                            help='Set epsilon = 1 to solve the non-linear issues.', required=False)
    results = arg_parser.parse_args(argv)
    results.file = results.file[0]
    results.out = results.file[0:results.file.rfind('.')] + '_t.c' if results.out is None else results.out
    results.function = results.function if results.function else os.path.splitext(os.path.basename(results.file))[0]

    logger.info('Parsing {}'.format(results.file))
    start = time.time()
    ast = parse_file(results.file, use_cpp=True, cpp_path='gcc', cpp_args=['-E'])
    transformer = LangTransformer(function_map=__FUNCTION_MAP, set_epsilon=results.epsilon)
    c_generator = CGenerator()

    with open(results.out, 'w') as f:
        # write verifier headers
        f.write(__HEADER)
        transformer.visit(ast)
        f.write(c_generator.visit(ast))
    logger.info('Transformation finished in {} seconds'.format(time.time() - start))
    start = time.time()
    is_verified = check(results.checker, results.out, results.function)
    if is_verified:
        logger.info('Verification finished in {} seconds'.format(time.time() - start))
    return is_verified


if __name__ == '__main__':
    main()
