#!/bin/sh
shadowdp examples/original/noisymax.c
shadowdp examples/original/sparsevector.c
# apply epsilon = 1 technique to solve non-linearity
shadowdp examples/original/diffsparsevector.c -e
shadowdp examples/original/partialsum.c -e
shadowdp examples/original/smartsum.c -e