#!/usr/bin/paython

__version__ = '1.0'

import time
from bc.validator import Validate as V
from bc import jsonrpc
from bc import log
from bc import customers
from bc import rates
from bc import tasks
from bc import polinomial

LOG = log.logger("wapi.tasks")
GROUPID = iter(polinomial.permutation())

@jsonrpc.method(
	validate = V({
			# Metric
			'type':		V(basestring),

			'customer':	V(basestring, min=36, max=36),

			'value':	V(int),

			# Info
			'user':		V(basestring, min=1,  max=64),
			'uuid':		V(basestring, min=36, max=36),
			'descr':	V(basestring),

			# Timings
			'time-create':	V(int, default=0),
			'time-destroy':	V(int, default=0),
	}),
	auth = False)
def taskAdd(request):
	""" Open new billing task """

	if request['time-create'] == 0:
		request['time-create'] = int(time.time())

	try:
		customer = customers.get(request['customer'])

		if not customer:
			return jsonrpc.result_error('InvalidParams',
				{ 'status': 'error', 'message': 'Invalid customer' })

		mid, rid, rate  = rates.resolve(request['type'], customer['tariff'])

		if not rid:
			return jsonrpc.result_error('InvalidParams',
				{ 'status': 'error', 'message': 'Unable to find rate' })

		t = tasks.Task(
			{
				'group_id':     GROUPID,
				'base_id':      request['uuid'],
				'customer':     customer['id'],

				'metric_id':    mid,
				'rate_id':      rid,
				'rate':         rate,

				'value':        request['value'],

				'time_create':  request['time-create'],
				'time_check':   request['time-create'],
				'time_destroy': request['time-destroy'],

				'target_user':  request['user'],
				'target_uuid':  request['uuid'],
				'target_descr': request['descr'],
			}
		)
		tasks.add(t)

	except Exception, e:
		LOG.exception("Unable to add new task: %s", e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to add new task' })

	return jsonrpc.result({'status':'ok'})


@jsonrpc.method(
	validate = V({
		'id':    V(basestring, min=36, max=36),
		'value': V(int),
		'user':  V(basestring, min=1,  max=64),
		'uuid':  V(basestring, min=36, max=36),
		'descr': V(basestring),
	}),
	auth = True)
def taskModify(request):
	try:
		t = tasks.Task({
			'base_id':      request['id'],
			'value':        request['value'],
			'target_user':  request['user'],
			'target_uuid':  request['uuid'],
			'target_descr': request['descr'],
		})
		tasks.update(t)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to modify task' })
	return jsonrpc.result({'status':'ok'})


@jsonrpc.method(
	validate = V({
		'id':           V(basestring, min=36, max=36),
		'time-destroy': V(int, default=0),
	}),
	auth = True)
def taskRemove(request):

	if request['time-destroy'] == 0:
		request['time-destroy'] = int(time.time())

	try:
		tasks.remove('id', request['id'], request['time-destroy'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to remove task' })

	return jsonrpc.result({ 'status':'ok' })
