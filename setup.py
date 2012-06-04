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
		'pymongo',
		'unittest2',
	],
	scripts     = [
		'bin/c2-bc-client',
		'bin/c2-bc-server',
		'bin/c2-bc-send'
	],
	package_dir = { '': 'lib' },
	packages    = [
		# Public interface
		'billing',

		# Billing library
		'bc',
		'bc/jsonrpc',
		'bc/private',
		'bc/wapi',
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
