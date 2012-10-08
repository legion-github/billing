#!/usr/bin/python

import re
import json
import cStringIO

from bc import utils

CONFIG = None
CONFIG_FILE = '/etc/billing.conf'

_TEMPLATE_CONFIG = {
	# Logger configuration
	'logging': {
		'type': 'syslog',
		'level': 'error',
		'logdir': '/var/log',
		'logsize': '30Mb',
		'backcount': 3,
		'address': '/dev/log',
		'facility': 'daemon'
	},

	"calc-server": {
		"pidfile": "/tmp/bc-calc.pid",
		"workers": 3
	},

	"data-server": {
		"pidfile": "/tmp/bc-data.pid",
		"source":      { "table": "bills",         "list": "@=database.shards" },
		"destination": { "table": "customerbills", "list": "@=zones" },
		"pusher": False,
	},

	"zone": {
		"local-DC": { "server": "localhost", "weight": 3, "local": True,
		              "auth": { "role": "admin", "secret": "qwerty" } }
	},

	# Database section
	"database": {
		# Database name
		"name": "billing",

		"user": "root",
		"pass": "",

		# Database searver for global collections
		"server": "127.0.0.1",

		# Database servers for sharding
		"shards": {}
	}
}

def _resolve_include(rootdict):
	def _include(d):
		for k,v in d.iteritems():
			if isinstance(v, dict):
				_include(v)
				continue

			if not isinstance(v, basestring) or v[:2] != '@=':
				continue

			d[k] = rootdict
			for e in v[2:].split('.'):
				d[k] = d[k][e]
		return d

	return _include(rootdict)


def read(filename = CONFIG_FILE, inline = None, force = False):
	"""Read system config file"""

	global CONFIG

	if CONFIG and not force:
		return CONFIG

	if isinstance(inline, basestring):
		f = cStringIO.StringIO(inline)
	else:
		f = open(filename, 'r')

	arrconf = []
	while True:
		line = f.readline()
		if not line:
			break

		# Remove trash from line
		line = re.sub(r'(^\s+|\s+$|\s*#.*$)', '', line)

		# Ignore empty string
		if line:
			arrconf.append(line)

	s = re.sub(r'([^,:\{\[])\s+("[^"\\]+":)', r'\1, \2', " ".join(arrconf))

	CONFIG = {}
	utils.dict_merge(CONFIG, _TEMPLATE_CONFIG, json.loads(s))
	_resolve_include(CONFIG)
	return CONFIG


def subdict(confdict, field='weight'):
	res = {}
	for k,v in confdict.iteritems():
		res[k] = v[field]
	return res

