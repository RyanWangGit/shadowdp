from shadowdp.__main__ import main


def test_main():
    assert main(['./examples/noisymax.c'])
