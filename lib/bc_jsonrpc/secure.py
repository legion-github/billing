#!/usr/bin/python
#
# secure.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
# Copyright (c) 2012-2013 by Nikolay Ivanov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#

__version__ = '1.0'

import base64, hmac, hashlib, string, time, fnmatch

try:
	from bc import database
	_HAVE_DATABASE = True
except ImportError:
	_HAVE_DATABASE = False


def serialize(data, prefix = 'params'):
	if not data:
		return [ prefix + " = null" ]
	res = []

	if isinstance(data, dict):
		for k in sorted(data.keys()):
			res.extend(serialize(data[k], prefix + '.' + str(k)))

	elif isinstance(data, list):
		i = 0
		for k in data:
			res.extend(serialize(data[i], prefix + '.' + str(i)))
			i += 1
	else:
		res.append(prefix + ' = ' + str(data))

	if prefix == 'params':
		return string.join(res,'\n')

	return res


def get_secret(role, method):
	if _HAVE_DATABASE:
		with database.DBConnect() as db:
			ret = db.find_one('auth',
				{
					'role': role,
					'method': method
				}
			)
			if ret:
				ret['found'] = True
				return ret
	field = '_invalid'
	return {
		'role':   field,
		'method': field,
		'secret': field,
		'host':   '*',
		'found':  False
	}


def sign_string(secret, string):
	""" Sign string using specified secret and return base64 encoded value """
	return base64.b64encode(hmac.new(str(secret), str(string), hashlib.sha1).digest())


def jsonrpc_is_auth(data):
	if not isinstance(data, dict):
		return False
	return set(['role','sign']) == set(data.keys())


def jsonrpc_auth(headers, sign, request):
	role   = sign.get('role', '')
	method = request.get('method', '')
	auth   = get_secret(role, method)

	if headers:
		for n in [ 'REMOTE_ADDR', 'REMOTE_HOST' ]:
			if n not in headers:
				continue
			if fnmatch.fnmatch(headers[n], auth['host']):
				break
		else:
			auth['found'] = False

	data = {
		'auth': {
			'role': auth['role']
		},
		'data': request
	}

	return ((sign.get('sign', '') == sign_string(auth['secret'], serialize(data))) and
	        (auth['found'] == True))


def jsonrpc_sign(role, secret, request):
	if 'params' not in request:
		request['params'] = {}

	data  = {
			'auth': {
				'role': role
			},
			'data': request
	}
	auth  = {
		'role': role,
		'sign': sign_string(secret, serialize(data))
	}

	if isinstance(request['params'], dict):
		request['params']['auth'] = auth

	elif isinstance(request['params'], list):
		request['params'].insert(0, auth)

	return request

