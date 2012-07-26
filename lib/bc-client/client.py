#!/usr/bin/env python

import httplib

from bc import log
from bc.jsonrpc import http
from bc.jsonrpc import message

LOG = log.logger("client", syslog=False)


class BillingError(Exception):
	def __init__(self, fmt, *args):
		Exception.__init__(self, fmt.format(*args))


ERRORS = dict((str(message.error_codes[i]['code']), BillingError(i)) for i in message.error_codes.keys())


class BCClient(object):
	def __init__(self, host, auth, timeout, methods_list):

		map(lambda x: setattr(self, x,
				lambda y={}: self.__request(x, y, host, auth, timeout)),
			methods_list)


	@staticmethod
	def __request(method, json_data, host, auth, timeout):
		def connect(host, timeout):
			try:
				conn = httplib.HTTPConnection(host, timeout = timeout)
				conn.connect()
				return conn
			except Exception as e:
				LOG.exception("Failed to connect to %s: %s.", host, e)

		def exceptionator(response):
			if 'result' in response.keys():
				return response['result']
			elif 'error'in response.keys():
				raise ERRORS[str(response['error']['code'])]

		try:
			response = http.jsonrpc_http_request(connect(host, timeout),
				method,
				json_data,
				auth_data=auth)
		except Exception as e:
			LOG.exception("Failed to communicate with Billing: %s", e)
		else:
			return exceptionator(response)

