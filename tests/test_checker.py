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
from shadowdp.checker import check


def test_check():
    assert check('./cpachecker', './examples/transformed/noisymax_t.c', 'noisymax')
    assert check('./cpachecker', './examples/transformed/sparsevector_t.c', 'sparsevector')
    assert check('./cpachecker', './examples/transformed/numsparsevector_rewrite.c', 'numsparsevector')
    assert check('./cpachecker', './examples/transformed/gapsparsevector_t.c', 'gapsparsevector')
    assert check('./cpachecker', './examples/transformed/partialsum_rewrite.c', 'partialsum')
    assert check('./cpachecker', './examples/transformed/prefixsum_t.c', 'prefixsum')
    assert check('./cpachecker', './examples/transformed/smartsum_rewrite.c', 'smartsum')

