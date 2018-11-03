from lang.checker import check


def test_check():
    assert check('./cpachecker', './examples/noisymax_t.c', 'noisymax')
