#!/usr/bin/python
#
# methods.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
# Copyright (c) 2012-2013 by Nikolay Ivanov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#

__version__ = '1.0'

import logging

import message
import secure

from bc.validator import ValidError

LOG = logging.getLogger("jsonrpc.methods")

JSONRPC_ERROR  = (01 << 1)
JSONRPC_RESULT = (01 << 2)
JSONRPC_HTTP   = (01 << 3)

methods = {}

def method_handler(method, validate = None, auth = True):
	""" Registers a public """

	methods[method.__name__.upper()] = { 'func': method, 'validator': validate, 'auth': bool(auth) }
	return method


def jsonrpc_method(validate = None, auth = True):
	""" Decorator for registering request methods """

	def wrap(method):
		return method_handler(method, validate, auth)
	return wrap


def jsonrpc_result(data):
	return (JSONRPC_RESULT, data)


def jsonrpc_result_error(errcode, data = None):
	return (JSONRPC_ERROR, errcode, data)


def jsonrpc_result_http(http_code, http_body = "", http_headers = []):
	return (JSONRPC_HTTP, http_code, http_body, http_headers)


def jsonrpc_process(headers, request):
	notification = 'id' not in request

	LOG.info(repr(request) + ": notification=" + str(notification))

	def error(errcode, data = None):
		if not notification:
			return message.jsonrpc_response_error(request, errcode, data)
		return None

	for n in ['jsonrpc','method']:
		if n not in request:
			return error('InvalidRequest')

	if request.get('method').upper() not in methods:
		return error('MethodNotFound')

	try:
		method = methods[request.get('method').upper()]
		params = request.get('params',None)

		if method['auth']:
			if isinstance(params, list) and len(params) > 0 and secure.jsonrpc_is_auth(params[0]):
				sign = params[0]
				params = params[1:]
				if not secure.jsonrpc_auth(headers, sign, request):
					return error('AuthFailure')

			elif isinstance(params, dict) and secure.jsonrpc_is_auth(params.get('auth',None)):
				sign = params['auth']
				del params['auth']
				if not secure.jsonrpc_auth(headers, sign, request):
					return error('AuthFailure')
			else:
				return error('AuthFailure')

		if method['validator']:
			params = method['validator'].check(params)

		res = method['func'](params)

		if notification or not res:
			return None

		if res[0] == JSONRPC_RESULT:
			return message.jsonrpc_response(request, res[1])

		if res[0] == JSONRPC_ERROR:
			return message.jsonrpc_response_error(request, res[1], res[2])

		if res[0] == JSONRPC_HTTP:
			return (res[1], res[2], res[3])

	except ValidError, e:
		return error('InvalidParams', str(e))

	except Exception, e:
		LOG.exception("Unable to process request", e)
		return error('InternalError')
