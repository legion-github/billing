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
		'aggregate':  V(int),
		'count_desc': V(basestring, min=1, max=64),
		'count_unit': V(int),
		'time_desc':  V(basestring, min=1, max=64),
		'time_unit':  V(int),
	}),
	auth = True)
def metricAdd(request):
	""" Adds new billing metric """

	try:
		m = metrics.Metric({
			'id':         request.get('id'),
			'type':       request.get('type'),
			'aggregate':  request.get('aggregate'),
			'count_desc': request.get('count_desc'),
			'count_unit': request.get('count_unit'),
			'time_desc':  request.get('time_desc'),
			'time_unit':  request.get('time_unit'),
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
