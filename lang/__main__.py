import argparse
import coloredlogs
import os.path
import sys
import time
import logging
from pycparser import parse_file
from pycparser.c_generator import CGenerator
from lang.core import LangTransformer
from lang.checker import check


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
    results = arg_parser.parse_args(argv)
    results.file = results.file[0]
    results.out = results.file[0:results.file.rfind('.')] + '_t.c' if results.out is None else results.out
    results.function = results.function if results.function else os.path.splitext(os.path.basename(results.file))[0]

    logger.info('Parsing {}'.format(results.file))
    start = time.time()
    ast = parse_file(results.file, use_cpp=True, cpp_path='gcc', cpp_args=['-E'])
    transformer = LangTransformer(function_map=__FUNCTION_MAP)
    c_generator = CGenerator()

    with open(results.out, 'w') as f:
        # write verifier headers
        f.write(__HEADER)
        transformer.visit(ast)
        f.write(c_generator.visit(ast))
    logger.info('Transformation finished in {} seconds'.format(time.time() - start))
    return check(results.checker, results.out, results.function)


if __name__ == '__main__':
    main()
