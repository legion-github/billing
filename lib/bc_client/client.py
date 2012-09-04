#!/usr/bin/env python

import httplib

from bc import log
from bc_jsonrpc import http
from bc_jsonrpc import message

LOG = log.logger("client", syslog=False)


class BillingError(Exception):
	def __init__(self, fmt, *args):
		Exception.__init__(self, fmt.format(*args))


ERRORS = dict((str(message.error_codes[i]['code']), lambda x: BillingError(i+': {0}', x)) for i in message.error_codes.keys())
ERRORS['0'] = lambda x: BillingError('Invalid return message')

class BCClient(object):
	def __init__(self, host, auth, timeout, methods_list):

		map(lambda x: setattr(self, x,
				lambda y={}: self.__request(x, y, host, auth, timeout, methods_list[1])),
			methods_list[0])


	@staticmethod
	def __request(method, json_data, host, auth, timeout, returning):
		def connect(host, timeout):
			try:
				conn = httplib.HTTPConnection(host, timeout = timeout)
				conn.connect()
				return conn
			except Exception as e:
				LOG.exception("Failed to connect to %s: %s.", host, e)
				raise e

		def exceptionator(response):
			if 'result' in response.keys():
				return response['result']
			elif 'error'in response.keys():
				raise ERRORS[str(response['error'].get('code', 0))](response['error'].get('data',{}).get('message', 0))

		try:
			response = http.jsonrpc_http_request(connect(host, timeout),
				method,
				json_data,
				auth_data=auth)
			return exceptionator(response).get(returning)
		except BillingError as e:
			LOG.exception("Failed to communicate with Billing: %s", e)
			raise e

