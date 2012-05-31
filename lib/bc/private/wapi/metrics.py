#!/usr/bin/paython

__version__ = '1.0'

from bc.private   import metrics
from bc.validator import Validate as V
from bc           import jsonrpc
from bc           import log

LOG = log.logger("wapi.metrics")

@jsonrpc.methods.jsonrpc_method(validate = False, auth = True)
def metricList(request):
	""" Returns a list of all registered metrics """

	try:
		ret = map(lambda m: m.values, metrics.get_all())

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to obtain metric list'
			}
		)
	return jsonrpc.methods.jsonrpc_result(
		{
			'status':'ok',
			'metrics': ret
		}
	)


@jsonrpc.methods.jsonrpc_method(
	validate = V({
		'id':         V(basestring, min=1, max=128),
		'type':       V(basestring, min=1, max=32),
		'formula':    V(basestring, min=1, max=32),
		'aggregate':  V(int),
	}),
	auth = True)
def metricAdd(request):
	""" Adds new billing metric """

	try:
		m = metrics.Metric({
			'id':         str(request.get('id')),
			'type':       str(request.get('type')),
			'formula':    str(request.get('formula')),
			'aggregate':  int(request.get('aggregate')),
		})
		metrics.add(m)
	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to add new metric'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })


@jsonrpc.methods.jsonrpc_method(
	validate = V({
		'id': V(basestring, min=1, max=128)
	}),
	auth = True)
def metricGet(request):
	""" Return metric object by name """

	try:
		m = metrics.get(request.get('id'))

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to get metric'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'metric': m.values, 'status':'ok' })
