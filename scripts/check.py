import os
import argparse
import subprocess


def check(path, filename, funcname):
    # check with MathSat
    mathsat = subprocess.Popen(
        ['./cpachecker/scripts/cpa.sh', '-predicateAnalysis', path, '-preprocess', '-entryfunction', funcname,
         '-setprop', 'cpa.predicate.encodeFloatAs=RATIONAL', '-setprop', 'solver.nonLinearArithmetic=USE'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # check with SMT-Interpol
    smtinterpol = subprocess.Popen(
        ['./cpachecker/scripts/cpa.sh', '-predicateAnalysis-linear', path, '-preprocess', '-entryfunction', funcname,
         '-setprop', 'solver.solver=smtinterpol'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # check with Z3
    z3 = subprocess.Popen(
        ['./cpachecker/scripts/cpa.sh', '-predicateAnalysis', path, '-preprocess', '-entryfunction', funcname,
         '-setprop', 'solver.solver=z3', '-setprop', 'cpa.predicate.encodeFloatAs=RATIONAL',
         '-setprop', 'solver.nonLinearArithmetic=USE'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    outputs = []
    is_verified = False
    for name, proc in zip(('SMT-Interpol', 'MathSat', 'Z3'), (smtinterpol, mathsat, z3)):
        out, err = proc.communicate()
        outputs.append((out, err))
        if r'Verification result: TRUE' in str(out):
            print('\033[0;1m{}\033[0m\033[92m verified with {}\033[0m'.format(filename, name))
            is_verified = True
            break

    if not is_verified:
        for name, (out, err) in zip(('SMT-Interpol', 'MathSat', 'Z3'), outputs):
            print('\033[31;1mCan\'t verify \033[0;1m{}\033[0m\033[31;1m, error message from {}:\033[0m'.format(filename, name))
            print(out)
            print(err)

    # kill all sub-processes
    for proc in (smtinterpol, mathsat, z3):
        proc.kill()
        proc.wait()

    return is_verified


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verify the transformed programs.')
    parser.add_argument('folder', metavar='folder', type=str, nargs=1,
                        help='The folder which contains transformed programs.')
    results = parser.parse_args()
    folder = results.folder[0]

    all_verified = True
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('_t.c'):
                if not check(os.path.join(root, file), file, file[:len(file) - 4]):
                    all_verified = False
    if all_verified:
        exit(0)
    else:
        exit(1)
