import os
import argparse
from lang.checker import check

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
                if not check('./cpachecker', os.path.join(root, file), file, file[:len(file) - 4]):
                    all_verified = False
    if all_verified:
        exit(0)
    else:
        exit(1)
