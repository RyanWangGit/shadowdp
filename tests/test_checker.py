from shadowdp.checker import check


def test_check():
    assert check('./cpachecker', './examples/noisymax_t.c', 'noisymax')
    assert check('./cpachecker', './examples/sparsevector_t.c', 'sparsevector')
    assert check('./cpachecker', './examples/partialsum_t.c', 'partialsum')
