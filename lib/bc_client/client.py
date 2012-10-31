#!/usr/bin/env python

from connectionpool import HTTPConnectionPool

from bc import log
from bc_jsonrpc import message
from bc_jsonrpc import http

LOG = log.logger("client", syslog=False)


class BillingError(Exception):
	def __init__(self, fmt, *args):
		Exception.__init__(self, fmt.format(*args))


ERRORS = dict((str(message.error_codes[i]['code']), lambda x: BillingError(i+': {0}', x)) for i in message.error_codes.keys())
ERRORS['0'] = lambda x: BillingError('Invalid return message')


class BCClient(object):
	def __init__(self, config):

		map(lambda x: setattr(self, x[0],
				lambda json={}, server=None: self.__request(x[0], json, x[1], server)),
			config.iteritems())
		try:
			self.pool = HTTPConnectionPool()
		except Exception as e:
			LOG.exception("Failed to connect: %s.", e)
			raise e

	def __request(self, method, json_data, info, server=None):

		def request(method, server, info):
			if ':' in server:
				host, port = server.split(':')
			else:
				host = server
				port = '80'
			return http.jsonrpc_http_request(self.pool,
				host, port, method, json_data,
				auth_data=info['hosts'][server])

		try:
			response = request(method, server if server else info['local'], info)

			if 'redirect' in response.keys():
				try:
					response = request(method, response['server'], info)
				except KeyError as e:
					LOG.exception("Redirect to unknown host: %s", response['server'])
					raise BillingError("Redirect to unknown server: {0}", response['server'])

			if 'result' in response.keys():
				return response['result'].get(info['returning'])
			elif 'error'in response.keys():
				raise ERRORS[str(response['error'].get('code', 0))](response['error'].get('message', 0))

		except BillingError as e:
			LOG.exception("Failed to communicate with Billing: %s", e)
			raise e

