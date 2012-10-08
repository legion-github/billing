#!/usr/bin/env python

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
	description = 'CROC Cloud Platform API library',
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
		'bin/billing-acl',
		'bin/billing-bootstrap',
		'bin/billing-init',
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
		('libexec/billing',     ['bin/httpd-abc']),
		('/etc',                ['data/billing.conf']),
		('/etc/httpd/conf.d',   ['data/httpd-abc.conf']),
		('/etc/rc.d/init.d',    ['data/init.d/c2-bc']),
		('/etc/cron.d',         dir_expand('data/cron.d')),
		('/usr/share/c2/gs',    dir_expand('data/gs')),
	],
)
