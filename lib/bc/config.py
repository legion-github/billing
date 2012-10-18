#!/usr/bin/python

import re
import ast

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
		"pusher": {},
	},

	"zones": {
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


def parse(astr, fn='<unknown>'):
	try:
		tree = ast.parse(astr, filename=fn, mode='eval')
	except SyntaxError as e:
		raise e

	boolean = {'true':'True', 'false':'False' }

	for node in ast.walk(tree):
		if not isinstance(node, (ast.Dict, ast.Expression, ast.List, ast.Load, ast.Name, ast.Num, ast.Str)):
			e = SyntaxError("Bad nodes found: {0}".format(node))
			e.filename, e.lineno = fn, node.lineno
			raise e

		if isinstance(node, ast.Name):
			if node.__dict__.get('id') in boolean:
				node.__dict__['id'] = boolean[node.__dict__['id']]

	return ast.literal_eval(tree)


def read(filename = CONFIG_FILE, inline = None, force = False):
	"""Read system config file"""

	global CONFIG

	if CONFIG and not force:
		return CONFIG

	fname   = '<inline>'
	confstr = inline

	if not isinstance(inline, basestring):
		fname   = filename
		confstr = open(fname).read()

	try:
		confstr = re.sub(r'^[ \t\n\r\f\v]+{', r'{', confstr)
		confstr = re.sub(r'}[ \t\n\r\f\v]+$', r'}', confstr)
		confdict = parse(confstr, fname)
	except SyntaxError as e:
		raise ValueError("Config file have syntax errors")

	CONFIG = {}
	utils.dict_merge(CONFIG, _TEMPLATE_CONFIG, confdict)
	_resolve_include(CONFIG)
	return CONFIG


def subdict(confdict, field='weight'):
	res = {}
	for k,v in confdict.iteritems():
		res[k] = v[field]
	return res

