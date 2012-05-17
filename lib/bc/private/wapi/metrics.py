#!/usr/bin/paython

__version__ = '1.0'

import uuid, logging

from bc.private   import metrics
from bc.validator import Validate as V
from bc           import jsonrpc

LOG = logging.getLogger("c2.abc")

@jsonrpc.methods.jsonrpc_method(validate = False, auth = False)
def metricList(environ, request):
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
		'type':        V(basestring, min=1, max=128),

		'count_name':  V(basestring, min=1, max=32),
		'count_value': V(int),

		'time_name':   V(basestring, min=1, max=32),
		'time_value':  V(int),
		'time_type':   V(int),

		'aggregate':   V(int),
	}),
	auth = False)
def metricAdd(environ, request):
	""" Adds new billing metric """

	try:
		m = metrics.Metric().set({
			'mtype': request.get('type'),
			'count_dimension': {
				'name':  request.get('count_name'),
				'value': request.get('count_value')
			},
			'time_dimension': {
				'name':  request.get('time_name'),
				'value': request.get('time_value')
			},
			'time_type': request.get('time_type'),
			'aggregate': request.get('aggregate')
		}).add()
	except:
		return jsonrpc.methods.jsonrpc_result_error('InvalidRequest', { 'status': 'error' })

	return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })


@jsonrpc.methods.jsonrpc_method(
	validate = V({
		'type': V(basestring, min=1, max=128)
	}),
	auth = False)
def metricGet(environ, request):
	""" Return metric object by name """

	try:
		m = metrics.Metric(request.get('type'))

	except ValueError:
		return jsonrpc.methods.jsonrpc_result_error('InvalidParams', { 'status': 'error' })

	return jsonrpc.methods.jsonrpc_result({ 'metric': m.values, 'status':'ok' })
