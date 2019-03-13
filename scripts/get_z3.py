# MIT License
#
# Copyright (c) 2018-2019 Yuxin (Ryan) Wang
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
import json
import sys
import os
import zipfile
import shutil
import string
import random
import urllib.request as urlrequest


def main():
    import argparse

    arg_parser = argparse.ArgumentParser(description=__doc__)
    arg_parser.add_argument('output_dir', metavar='OUTPUT_DIR', type=str, nargs='?', default='./')

    results = arg_parser.parse_args()

    if os.path.exists(results.output_dir + '/z3'):
        exit('z3 folder exists in ' + os.path.abspath(results.output_dir))

    # detect os name
    system = sys.platform
    library_files = ['.txt']
    if 'linux' in system:
        system = 'ubuntu-14.04'
        library_files.append('libz3.so')
        library_files.append('libz3java.so')
    elif 'darwin' in system:
        system = 'osx'
        library_files.append('libz3.dylib')
        library_files.append('libz3java.dylib')
    elif 'windows' in system:
        system = 'win'
        library_files.append('Microsoft.Z3.dll')
        library_files.append('Microsoft.Z3.xml')

    # append java-related library files
    library_files.append('com.microsoft.z3.jar')

    # read from GitHub apis
    releases = json.loads(urlrequest.urlopen('https://api.github.com/repos/Z3Prover/z3/releases')
                          .read().decode('utf-8'))[0]

    for asset in releases['assets']:
        if system in asset['name'] and 'x64' in asset['name']:
            # find a random non-conflict tmp folder name
            tmp_folder = './tmp'
            while os.path.exists(tmp_folder):
                tmp_folder = './' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

            # download the release zip file
            os.mkdir(tmp_folder)
            os.mkdir(tmp_folder + '/z3')

            def progress(count, block_size, total_size):
                percent = (count * block_size) / total_size
                progress_count = int(percent * 30)
                dot_count = 30 - progress_count - 1
                sys.stdout.write('Downloading %s ' % releases['name'])
                sys.stdout.write('[' + progress_count * '=' + '>' +
                                 dot_count * '.' + '] ' + '{: >3d}'.format(int(percent * 100)) + '%\r')
                sys.stdout.flush()

            urlrequest.urlretrieve(asset['browser_download_url'], tmp_folder + '/z3.zip', progress)
            print('Downloading %s...' % releases['name'] + '[' + 29 * '=' + '>] 100%')

            print('Download finished. Extracting files...')
            zf = zipfile.ZipFile(tmp_folder + '/z3.zip')
            zf.extractall(tmp_folder)

            for file in zf.namelist():
                # move the license file, java bindings and corresponding library
                for library_file in library_files:
                    if file.endswith(library_file):
                        shutil.move(tmp_folder + '/' + file, results.output_dir + '/' + file[file.rfind('/'):])

            print('Extract finished, Removing temporary files...')
            shutil.rmtree(tmp_folder)
            print('Done.')
            break


if __name__ == '__main__':
    main()
