#!/bin/sh
shadowdp examples/original/noisymax.c
echo ''
shadowdp examples/original/sparsevector.c
echo ''
# apply epsilon = 1 technique to solve non-linearity
shadowdp examples/original/diffsparsevector.c -e
echo ''
shadowdp examples/original/partialsum.c -e
echo ''
shadowdp examples/original/smartsum.c -e