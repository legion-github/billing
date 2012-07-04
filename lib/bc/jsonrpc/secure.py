#!/usr/bin/python

__version__ = '1.0'

import base64, hmac, hashlib, logging, string, time, fnmatch
from bc import database

LOG = logging.getLogger("jsonrpc.auth")

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
	with database.DBConnect() as db:
		return db.find_one('auth',
			{
				'role': role,
				'method': method
			}
		)


def sign_string(secret, string):
	""" Sign string using specified secret and return base64 encoded value """
	return base64.b64encode(hmac.new(secret, string, hashlib.sha1).digest())


def jsonrpc_is_auth(data):
	if not isinstance(data, dict):
		return False
	return set(['role','sign']) == set(data.keys())


def jsonrpc_auth(headers, sign, request):
	role   = sign.get('role')
	method = request.get('method')
	auth   = get_secret(role, method)

	if not auth or not auth['secret'] or not auth['host']:
		return False

	if headers:
		for n in [ 'REMOTE_ADDR', 'REMOTE_HOST' ]:
			if n not in headers:
				continue
			if fnmatch.fnmatch(headers[n], auth['host']):
				break
		else:
			return False

	data  = {
			'auth': {
				'role': role,
				'time': int(time.time()) / 15 * 15
			},
			'data': request
	}
	return sign.get('sign') == sign_string(str(auth['secret']), serialize(data))


def jsonrpc_sign(role, secret, request):
	if 'params' not in request:
		request['params'] = {}

	data  = {
			'auth': {
				'role': role,
				'time': int(time.time()) / 15 * 15
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

