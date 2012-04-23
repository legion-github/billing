#!/usr/bin/python

__version__ = '1.0'

__all__ = [ 'MAX_REQUEST_SIZE', 'jsonrpc_handle' ]

import json
import logging

from bc.jsonrpc import methods

LOG = logging.getLogger("jsonrpc.wsgi")

MAX_REQUEST_SIZE = 1024 * 1024 # 1 Mb
"""Maximum request size."""


def jsonrpc_handle(environ, start_response):
	"""Handles an HTTP request."""

	def answer(http_code, http_body = '', http_headers = []):
		start_response(http_code, http_headers)
		return http_body

	if not environ.get("CONTENT_LENGTH"):
		return answer("411 Length Required")

	request_length = int(environ["CONTENT_LENGTH"])

	if request_length > MAX_REQUEST_SIZE:
		return answer('400 Bad Request')

	try:
		response = ""
		request_body = environ["wsgi.input"].read(request_length)

		for r in request_body.split('\n'):
			if not r:
				continue

			result = methods.jsonrpc_process(json.loads(r))

			if not result:
				continue

			if isinstance(result, tuple):
				return answer(result[0], result[1], result[2])

			response += json.dumps(result) + "\n"

		return answer("200 OK", response)

	except Exception,e:
		LOG.exception("Failed handle request")
		return answer('500 Internal Server Error')
