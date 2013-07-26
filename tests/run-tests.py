#!/usr/bin/python
#
# run-tests.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
# Copyright (c) 2012-2013 by Nikolay Ivanov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#

import os
import sys
import glob
import imp
import unittest2 as unittest

sys.path.insert(0, '../lib')

from bc import log

suite = unittest.TestSuite()

LOG = log.logger("unittests", type='stderr', level='debug', init=True)

for testpath in sorted(glob.glob('./test_*.py')):
	name = os.path.basename(testpath)[:-3]

	if len(sys.argv) > 1:
		if name not in sys.argv[1:] and name + '.py' not in sys.argv[1:]:
			continue

	test = imp.load_source(name, testpath)
	suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test.Test))

result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(not result.wasSuccessful())
