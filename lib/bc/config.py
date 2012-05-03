#!/usr/bin/python

import re
import json
import string
import cStringIO

from bc import utils

CONFIG = None
CONFIG_FILE = '/etc/billing.conf'

_TEMPLATE_CONFIG = {
	# Logger configuration
	'logging': {
		'level':  'error',
		'logdir': '/var/log',
	},

	# Database section
	"database": {
		# Database name
		"name": "billing",

		# Database searver for global collections
		"server": "127.0.0.1",

		# Database servers for sharding
		"shards": []
	}
}

def read(filename = CONFIG_FILE, inline = None, force = False):
	"""Read system config file"""

	global CONFIG

	if CONFIG and not force:
		return CONFIG

	arrconf = []
	pattern_trash = re.compile('(^\s+|\s+$|\s*#.*$)')

	if isinstance(inline, basestring):
		f = cStringIO.StringIO(inline)
	else:
		f = open(filename, 'r')

	while True:
		line = f.readline()
		if not line:
			break

		# Remove tailing '\n'
		line = line[:-1]

		# Remove trash from line
		line = re.sub(pattern_trash, '', line)

		# Ignore empty string
		if not line:
			continue

		arrconf.append(line)

	CONFIG = utils.dict_merge(_TEMPLATE_CONFIG, json.loads(string.join(arrconf, ' ')))
	return CONFIG
