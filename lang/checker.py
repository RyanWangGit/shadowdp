from collections import OrderedDict
import subprocess
import logging
logger = logging.getLogger(__name__)


def check(checkerpath, path, funcname):
    processes = OrderedDict()
    processes['MathSat'] = subprocess.Popen(
        [checkerpath + '/scripts/cpa.sh', '-predicateAnalysis', path, '-preprocess', '-entryfunction', funcname,
         '-setprop', 'cpa.predicate.encodeFloatAs=RATIONAL', '-setprop', 'solver.nonLinearArithmetic=USE'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    processes['Z3'] = subprocess.Popen(
        [checkerpath + '/scripts/cpa.sh', '-predicateAnalysis', path, '-preprocess', '-entryfunction', funcname,
         '-setprop', 'solver.solver=z3', '-setprop', 'cpa.predicate.encodeFloatAs=RATIONAL',
         '-setprop', 'solver.nonLinearArithmetic=USE'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    processes['SMTInterpol'] = subprocess.Popen(
        [checkerpath + '/scripts/cpa.sh', '-predicateAnalysis-linear', path, '-preprocess', '-entryfunction', funcname,
         '-setprop', 'solver.solver=smtinterpol'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    outputs = []
    is_verified = False
    for name, proc in processes.items():
        # wait for 30 seconds
        try:
            if not is_verified:
                out, err = proc.communicate(timeout=30)
                outputs.append((name, out, err))
                if r'Verification result: TRUE' in str(out):
                    logger.info('{} verified with {}.'.format(path, name))
                    is_verified = True
                    break
        except subprocess.TimeoutExpired:
            continue
        finally:
            proc.kill()
            proc.wait()

    # if no solvers can verify the program
    if not is_verified:
        for name, out, err in outputs:
            logger.debug('No solvers can verify the program, error messages shown below:')
            logger.debug('{}:\n\tout: {}\n\t{}'.format(name, out, err))

    return is_verified
