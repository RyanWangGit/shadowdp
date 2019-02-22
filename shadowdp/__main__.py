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
coloredlogs.install(level='INFO', fmt='%(levelname)s:%(module)s: %(message)s')

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
                            action='store_true', dest='epsilon', default=False,
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
        content = c_generator.visit(ast)
        # replace the non-linearity
        if 'partialsum' in results.file:
            content = content.replace('float __LANG_v_epsilon = 0;', 'float __LANG_v_epsilon = 0;\n\tfloat __LANG_distance_sum=0;')
            insert = """if (i == __LANG_index)
        __VERIFIER_assume (__LANG_distance_q[i] >= -1 && __LANG_distance_q[i] <= 1);
    else
        __VERIFIER_assume (__LANG_distance_q[i] == 0);\n\t"""
            content = content.replace('sum = sum + q[i];', insert + 'sum = sum + q[i];\n\t__LANG_distance_sum = __LANG_distance_sum + __LANG_distance_q[i];')
        elif 'smartsum' in results.file:
            content = content.replace('__LANG_v_epsilon = __LANG_v_epsilon + (__LANG_distance_sum + (__LANG_distance_q[i] * (1 / (1.0 / 1.0))));', """if (i == __LANG_index)
      {
        __VERIFIER_assume(__LANG_distance_q[i] <= 1 && __LANG_distance_q[i] >= -1);
        __LANG_v_epsilon = __LANG_v_epsilon + abs(__LANG_distance_sum + __LANG_distance_q[i]);
      }
      else
      {
        __VERIFIER_assume(__LANG_distance_q[i] == 0);
        __LANG_v_epsilon = __LANG_v_epsilon + __LANG_distance_sum;
      }""")
            content = content.replace('__LANG_v_epsilon = __LANG_v_epsilon + (1.0 * __LANG_distance_sum);',"""if (i == __LANG_index)
      {
        __VERIFIER_assume(__LANG_distance_q[i] <= 1 && __LANG_distance_q[i] >= -1);
        __LANG_v_epsilon = __LANG_v_epsilon + abs(__LANG_distance_q[i]);
      }
      else
      {
        __VERIFIER_assume(__LANG_distance_q[i] == 0);
        __LANG_v_epsilon = __LANG_v_epsilon + __LANG_distance_q[i];
      }""")
            content = content.replace('__LANG_distance_sum = __LANG_distance_sum + __LANG_distance_q[i];', '__LANG_distance_sum = __LANG_distance_sum + abs(__LANG_distance_q[i]);')
            content = content.replace('(((__LANG_distance_n + __LANG_distance_sum) + __LANG_distance_q[i]) + __LANG_distance_sum) + __LANG_distance_q[i]', '__LANG_distance_n')
            content = content.replace('__LANG_distance_next = (__LANG_distance_next + __LANG_distance_q[i]) + __LANG_distance_sum;', '__LANG_distance_next = __LANG_distance_next;')
            content = content.replace('__LANG_distance_out = (__LANG_distance_next + __LANG_distance_q[i]) + __LANG_distance_sum;', '__LANG_distance_out = __LANG_distance_next;')
            content = content.replace('__VERIFIER_assert(__LANG_v_epsilon <= 1.0);', '__VERIFIER_assert(__LANG_v_epsilon <= 2.0);')
            content = content.replace('__VERIFIER_assume(size > 0);', '__VERIFIER_assume(size > 0);\n  __VERIFIER_assume(T < size && T > 0);\n  __VERIFIER_assume(M > 0 && M < size);')
        elif 'diffsparsevector' in results.file:
            content = content.replace('__LANG_v_epsilon = __LANG_v_epsilon + (((q[i] + eta_2) >= T_bar) ? (1 - (__LANG_distance_q[i] * (1 / ((4.0 * 1) / 1.0)))) : (0));', '__LANG_v_epsilon = __LANG_v_epsilon + (((q[i] + eta_2) >= T_bar) ? (0.5 * 1) : (0));')
        f.write(content)

    logger.info('Transformation finished in {} seconds'.format(time.time() - start))
    start = time.time()
    is_verified = check(results.checker, results.out, results.function)
    if is_verified:
        logger.info('Verification finished in {} seconds'.format(time.time() - start))
    return is_verified


if __name__ == '__main__':
    main()
