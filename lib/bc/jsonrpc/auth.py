#!/usr/bin/python

__version__ = '1.0'

__all__ = [ 'jsonrpc_is_auth', 'jsonrpc_auth', 'jsonrpc_sign_request' ]

import base64, hmac, hashlib, uuid, logging, string
from bc import mongodb

LOG = logging.getLogger("jsonrpc.auth")

def serialize(data, prefix = 'params'):
	if not data:
		return prefix + " = null"
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
	o = mongodb.collection('auth_roles').find_one(
		{ 'role': role, 'method': method },
		fields = { 'secret': True }
	)
	if not o:
		return None
	return o['secret']


def sign_string(secret, string):
	""" Sign string using specified secret and return base64 encoded value """
	return base64.b64encode(hmac.new(secret, string, hashlib.sha1).digest())


def jsonrpc_is_auth(data):
	if not isinstance(data, dict):
		return False
	return set(['role','sign']) == set(data.keys())


def jsonrpc_auth(sign, request):
	role   = sign.get('role')
	method = request.get('method')
	secret = get_secret(role, method)

	if not secret:
		return False

	return sign.get('sign') == sign_string(str(secret), str(serialize(request)))


def jsonrpc_sign(role, secret, request):
	auth = {
		'role': role,
		'sign': sign_string(secret, serialize(request))
	}

	if 'params' not in request:
		request['params'] = {}

	if isinstance(request['params'], dict):
		request['params']['auth'] = auth

	elif isinstance(request['params'], list):
		request['params'].insert(0, auth)

	return request

