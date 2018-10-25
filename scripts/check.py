import os
import argparse
import subprocess


def check(path, filename, funcname):
    print('\033[92mChecking \033[0;1m{}\033[0m \033[92mwith \033[31;1mMathSat\033[0m'.format(filename))
    subprocess.call(
        ['./cpachecker/scripts/cpa.sh', '-predicateAnalysis-linear', path, '-preprocess', '-entryfunction', funcname])
    print('\033[92mChecking \033[1m{}\033[0m \033[92mwith \033[31;1mSMT-Interpol\033[0m'.format(filename))
    subprocess.call(
        ['./cpachecker/scripts/cpa.sh', '-predicateAnalysis-linear', path, '-preprocess', '-entryfunction', funcname,
         '-setprop', 'solver.solver=smtinterpol'])
    print('\033[92mChecking \033[1m{}\033[0m \033[92mwith \033[31;1mZ3\033[0m'.format(filename))
    subprocess.call(
        ['./cpachecker/scripts/cpa.sh', '-predicateAnalysis-linear', path, '-preprocess', '-entryfunction', funcname,
         '-setprop', 'solver.solver=z3'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verify the transformed programs.')
    parser.add_argument('folder', metavar='folder', type=str, nargs=1,
                        help='The folder which contains transformed programs.')
    results = parser.parse_args()
    folder = results.folder[0]

    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('_t.c'):
                check(os.path.join(root, file), file, file[:len(file) - 4])
