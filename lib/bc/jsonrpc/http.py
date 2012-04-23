__version__ = '1.0'

__all__ = ['JsonRpcHttpError', 'jsonrpc_http_request']

import json
import httplib

from bc.jsonrpc import auth
from bc.jsonrpc import message

class JsonRpcHttpError(Exception):
	def __init__(self, fmt, *args):
		Exception.__init__(self, fmt.format(*args))


def jsonrpc_http_request(conn, method, params, auth_data = None, req_limit = 256):
	req = message.jsonrpc_request(method, params)

	if auth_data:
		req = auth.jsonrpc_sign(auth_data['role'], auth_data['secret'], req)

	conn.request("POST", "/", json.dumps(req))
	response = conn.getresponse()

	if response.status != httplib.OK:
		raise JsonRpcHttpError("The server returned an error: {0}.", response.reason)

	reply = response.read(req_limit + 1)

	if len(reply) > req_limit:
		raise JsonRpcHttpError("Got a reply of too big size.")

	res = json.loads(reply)

	if not message.jsonrpc_is_response(res):
		raise JsonRpcHttpError("Got wrong response: {0}.", repr(res))

	if res['id'] != req['id']:
		raise JsonRpcHttpError("Got wrong reply id: {0}.", repr(res))

	if 'error' in res:
		raise JsonRpcHttpError("Remote error: {0}.", repr(res['error']))

	if 'status' not in res['result'] or res['result']['status'] != 'ok':
		raise JsonRpcHttpError("Something bad: {0}.", repr(res))

	return res
