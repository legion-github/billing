#!/usr/bin/python
#
# http://en.wikipedia.org/wiki/Permutation_polynomial

import random

p = 24
n = 2**p

print n

c = random.randint(0, n)
ave = 0
for j in xrange(n - 1):
	i1 = (2 * p * j * j + j + c) % n
	i2 = (2 * p * (j + 1) * (j + 1) + (j + 1) + c) % n
	diff = abs(i2 - i1)
	ave += diff
ave = ave / n
print ave
