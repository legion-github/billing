#!/usr/bin/python

# http://en.wikipedia.org/wiki/JSON-RPC
# http://jsonrpc.org/spec.html

__version__ = '1.0'

__all__ = [
	'jsonrpc_request', 'jsonrpc_notify', 'jsonrpc_response', 'jsonrpc_response_error',
	'jsonrpc_is_response', 'jsonrpc_is_request', 'jsonrpc_is_notification'
]

import uuid, logging

LOG = logging.getLogger("jsonrpc.message")

jsonrpc_version = '2.0'

error_codes = {
	'ParseError': {
		# Invalid JSON was received by the server.
		# An error occurred on the server while parsing the JSON text.
		'code': -32700, 'message': 'Parse error'
	},
	'InvalidRequest': {
		# The JSON sent is not a valid Request object.
		'code': -32600, 'message': 'Invalid Request'
	},
	'MethodNotFound': {
		# The method does not exist / is not available.
		'code': -32601, 'message': 'Method not found'
	},
	'InvalidParams': {
		# Invalid method parameter(s).
		'code': -32602, 'message': 'Invalid params'
	},
	'InternalError': {
		# Internal JSON-RPC error.
		'code': -32603, 'message': 'Internal error'
	},
	'ServerError': {
		# Reserved for implementation-defined server-errors. (-32000 to -32099)
		'code': -32000, 'message': 'Server error'
	},
	'AuthFailure': {
		'code': -32001, 'message': 'Authentication failure'
	}
}

def jsonrpc_is_response(data):
	""" Checks data is valid JSON-RPC 2.0 response """

	if not isinstance(data, dict):
		return False

	for n in ['jsonrpc', 'id']:
		if n not in data:
			return False

	if data['jsonrpc'] != jsonrpc_version:
		return False

	if 'error' in data:
		if 'result' in data:
			return False

		for n in ['code', 'message']:
			if n not in data['error']:
				return False

		for e in error_codes.itervalues():
			if data['error']['code'] == e['code']:
				break
		else:
			return False
	elif 'result' in data:
		if 'error' in data:
			return False
	else:
		return False

	return True


def jsonrpc_is_request(data):
	""" Checks data is valid JSON-RPC 2.0 request """

	if not isinstance(data, dict):
		return False

	for n in ['jsonrpc', 'method', 'id']:
		if n not in data:
			return False

	if data['jsonrpc'] != jsonrpc_version:
		return False

	if not isinstance(data['id'], (int,long,basestring)):
		return False

	return True


def jsonrpc_is_notification(data):
	""" Checks data is valid JSON-RPC 2.0 notification """

	if not isinstance(data, dict):
		return False

	for n in ['jsonrpc', 'method']:
		if n not in data:
			return False

	if data['jsonrpc'] != jsonrpc_version:
		return False

	if 'id' in data:
		return False

	return True


def response(request, **kwargs):
	""" Lowlevel response generator """

	r = {
		'jsonrpc': jsonrpc_version,
		'id': request.get('id', None)
	}

	for n in ['result', 'error']:
		if n in kwargs:
			r[n] = kwargs.get(n)
	return r


def jsonrpc_response_error(request, errcode, data = None):
	""" Generates error response """

	if not errcode or errcode not in error_codes:
		errcode = 'InternalError'

	e = dict(error_codes.get(errcode))
	if data:
		e['data'] = data
	return response(request, error = e)


def jsonrpc_response(request, data):
	""" Generates result response """
	return response(request, result = data)


def request(**kwargs):
	r = {
		'jsonrpc': jsonrpc_version,
		'method': kwargs.get('method'),
	}
	for n in ['id', 'params']:
		if n in kwargs and kwargs.get(n) != None:
			r[n] = kwargs.get(n)
	return r


def jsonrpc_notify(method, params):
	return request(
		method = method,
		params = params)


def jsonrpc_request(method, params):
	return request(
		method = method,
		params = params,
		id = str(uuid.uuid4()))
