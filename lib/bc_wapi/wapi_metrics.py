#
# wapi_metrics.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
# Copyright (c) 2012-2013 by Nikolay Ivanov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#

__version__ = '1.0'

import bc_jsonrpc as jsonrpc

from bc.validator import Validate as V
from bc import metrics
from bc import log

LOG = log.logger("wapi.metrics")

@jsonrpc.method(validate = False, auth = True)
def metricList(request):
	""" Returns a list of all registered metrics """

	try:
		ret = map(lambda m: m.values, metrics.get_all())

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to obtain metric list' })

	return jsonrpc.result({ 'status': 'ok', 'metrics': ret })


@jsonrpc.method(
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
		m = metrics.Metric(request)
		metrics.add(m)
	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to add new metric' })

	return jsonrpc.result({ 'status':'ok', 'id':m.id })


@jsonrpc.method(
	validate = V({
		'id': V(basestring, min=1, max=128)
	}),
	auth = True)
def metricGet(request):
	""" Return metric object by name """

	try:
		ret = metrics.get(request.get('id'))

		if not ret:
			return jsonrpc.result_error('InvalidRequest',
				{ 'status': 'error', 'message': 'Metric not found' })

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to obtain metric' })

	return jsonrpc.result({ 'status': 'ok', 'metric': ret.values })
