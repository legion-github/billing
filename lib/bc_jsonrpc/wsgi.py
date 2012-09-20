#!/usr/bin/python

__version__ = '1.0'

import json
import logging

import methods

LOG = logging.getLogger("jsonrpc.wsgi")

MAX_REQUEST_SIZE = 1024 * 1024 # 1 Mb
"""Maximum request size."""

HTTP_CGI_HEADERS = [
	"DOCUMENT_ROOT", "HTTP_ACCEPT", "HTTP_ACCEPT_ENCODING", "HTTP_HOST",
	"AUTH_TYPE", "CONTENT_LENGTH", "CONTENT_TYPE", "GATEWAY_INTERFACE",
	"PATH_INFO", "PATH_TRANSLATED", "QUERY_STRING", "REMOTE_ADDR",
	"REMOTE_HOST", "REMOTE_IDENT", "REMOTE_USER", "REQUEST_METHOD",
	"SCRIPT_NAME", "SERVER_NAME", "SERVER_PORT", "SERVER_PROTOCOL",
	"SERVER_SOFTWARE"
]


def jsonrpc_handle(environ, start_response):
	"""Handles an HTTP request."""

	def answer(http_code, http_body = '', http_headers = []):
		start_response(http_code, http_headers)
		return http_body

	if "CONTENT_LENGTH" not in environ:
		return answer("411 Length Required")

	request_length = int(environ["CONTENT_LENGTH"])

	if request_length <= 0 or request_length > MAX_REQUEST_SIZE:
		return answer('400 Bad Request')

	headers = {}
	for n,v in environ.iteritems():
		if n in HTTP_CGI_HEADERS or n.startswith("X_"):
			headers[n] = v

	try:
		response = ""
		request_body = environ["wsgi.input"].read(request_length)

		for r in request_body.split('\n'):
			if not r:
				continue

			result = methods.jsonrpc_process(headers, json.loads(r))

			if not result:
				continue

			if isinstance(result, tuple):
				return answer(result[0], result[1], result[2])

			response += json.dumps(result) + "\n"

		return answer("200 OK", response)

	except Exception,e:
		LOG.exception("Failed handle request")
		return answer('500 Internal Server Error')
