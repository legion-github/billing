__version__ = '1.0'

import bc_jsonrpc as jsonrpc

from bc.validator import Validate as V
from bc import sync
from bc import log

LOG = log.logger("wapi.sync")


@jsonrpc.method(
	validate = V({
		'table':  V(basestring, min=3, max=36),
		'record': V(dict),
	}),
	auth = True)
def sync(params):
	try:
		sync.record(params['table'], params['record'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to sync object' })

	return jsonrpc.result({ 'status':'ok' })


@jsonrpc.method(
	validate = V({
		'table': V(basestring, min=3, max=36),
		'list':  V(list),
	}),
	auth = True)
def syncList(params):
	try:
		for r in params['list']:
			sync.record(params['table'], r)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to sync list of objects' })

	return jsonrpc.result({ 'status':'ok' })
