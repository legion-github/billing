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

	ret = []
	for m in metrics.get_all():
		ret.append(m.values)

	return jsonrpc.methods.jsonrpc_result(
		{
			'metrics': ret,
			'status':'ok'
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
			'id':         request.get('id'),
			'type':       request.get('type'),
			'formula':    request.get('formula'),
			'aggregate':  request.get('aggregate'),
		})
		metrics.add(m)
	except:
		return jsonrpc.methods.jsonrpc_result_error('InvalidRequest', { 'status': 'error' })

	return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })


@jsonrpc.methods.jsonrpc_method(
	validate = V({
		'id': V(basestring, min=1, max=128)
	}),
	auth = True)
def metricGet(request):
	""" Return metric object by name """

	try:
		m = metrics.Metric(request.get('type'))

	except ValueError:
		return jsonrpc.methods.jsonrpc_result_error('InvalidParams', { 'status': 'error' })

	return jsonrpc.methods.jsonrpc_result({ 'metric': m.values, 'status':'ok' })
