#!/usr/bin/env python
#
# setup.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
# Copyright (c) 2012-2013 by Nikolay Ivanov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#

import os
try:
	from setuptools import setup
except ImportError:
	from distutils import setup


def dir_expand(path):
	return map(lambda n: path + '/' + n, os.listdir(path))

setup(
	name        = 'python-billing',
	version     = '1.0',
	description = 'Billing Platform',
	license     = 'GPLv3',
	platforms   = 'Linux',
	author      = 'Alexey Gladkov',
	author_email= 'gladkov.alexey@gmail.com',
	requires    = [
		'msgpack',
		'psycopg2',
		'unittest2',
		'connectionpool',
	],
	scripts     = [
		'bin/bc-calc-client',
		'bin/bc-calc-server',

		'bin/bc-data-pusher',
		'bin/bc-data-routine',
		'bin/bc-data-server',
		'bin/bc-data-withdraw',

		'bin/billing-acl',
		'bin/billing-bootstrap',
		'bin/billing-init',

		'bin/task_creator',
	],
	package_dir = { '': 'lib' },
	packages    = [
		# Public interface
		'bc_client',

		# Billing library
		'bc',
		'bc_jsonrpc',
		'bc_wapi',
	],
	data_files  = [
		('libexec/bc',          ['bin/httpd-wapi']),
		('/etc',                ['data/billing.conf','data/wapi-acl.conf']),
		('/etc/httpd/conf.d',   ['data/httpd-wapi.conf']),
		('/etc/rc.d/init.d',    ['data/init.d/bc-calc','data/init.d/bc-data']),
		('/etc/cron.d',         dir_expand('data/cron.d')),
		('/usr/share/c2/gs',    dir_expand('data/gs')),
	],
)
