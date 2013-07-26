#!/usr/bin/python
#
# polinomial.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#

__version__ = '1.0'

import random

def permutation(p=2, k=16, loop=True):
	"""Permutation polynomial

	Consider g(x) = ax^2+bx+c for the ring Z/p^kZ.

	Lemma: for k>1 (Z/p^kZ) such polynomial defines a permutation if and only if
	a=0 mod p and b!=0 mod p.

	URL: http://en.wikipedia.org/wiki/Permutation_polynomial

	Arguments 'p' and 'k' defines sequence p^k.
	Argument 'loop' leads to an infinite sequence.
	"""

	n = p**k

	do = True
	while do:
		r1 = random.randint(1, n**2)
		r2 = random.randint(1, n**2)
		r3 = random.randint(0, n)

		a = r1*p
		b = r2*p-1
		c = r3

		#print "y = x * ({0} * x + {1}) + {2}".format(a,b,c)

		for i in xrange(0, n):
			yield ( i*( a*i + b ) + c ) % n

		do = loop
