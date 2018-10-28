import os
import argparse
import subprocess


def check(path, filename, funcname):
    # check with MathSat
    mathsat = subprocess.Popen(
        ['./cpachecker/scripts/cpa.sh', '-predicateAnalysis', path, '-preprocess', '-entryfunction', funcname,
         '-setprop', 'cpa.predicate.encodeFloatAs=RATIONAL', '-setprop', 'solver.nonLinearArithmetic=USE'])
    # check with SMT-Interpol
    smtinterpol = subprocess.Popen(
        ['./cpachecker/scripts/cpa.sh', '-predicateAnalysis-linear', path, '-preprocess', '-entryfunction', funcname,
         '-setprop', 'solver.solver=smtinterpol'])
    # check with Z3
    z3 = subprocess.Popen(
        ['./cpachecker/scripts/cpa.sh', '-predicateAnalysis', path, '-preprocess', '-entryfunction', funcname,
         '-setprop', 'solver.solver=z3', '-setprop', 'cpa.predicate.encodeFloatAs=RATIONAL',
         '-setprop', 'solver.nonLinearArithmetic=USE'])

    outputs = []
    is_verified = False
    for name, proc in zip(('SMT-Interpol', 'MathSat', 'Z3'), (smtinterpol, mathsat, z3)):
        out, err = proc.communicate()
        outputs.append((out, err))
        if r'Verification result: TRUE' in out:
            print('Verified with {}'.format(name))
            is_verified = True
            break

    if not is_verified:
        for name, (out, err) in zip(('SMT-Interpol', 'MathSat', 'Z3'), outputs):
            print('Error message from {}:'.format(name))
            print(out)
            print(err)

    # kill all sub-processes
    for proc in (smtinterpol, mathsat, z3):
        proc.kill()
        proc.wait()


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
