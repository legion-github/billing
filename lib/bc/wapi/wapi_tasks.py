#!/usr/bin/paython

__version__ = '1.0'

from bc.validator import Validate as V
from bc import jsonrpc
from bc import log
from bc import customers
from bc import queue
from bc import tasks

LOG = log.logger("wapi.tasks")

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

		rid, rate  = queue.resolve(request['type'], customer['tariff'])

		if not rid:
			return jsonrpc.result_error('InvalidParams',
				{ 'status': 'error', 'message': 'Unable to find rate' })

		t = tasks.Task(
			{
				'id':           request['uuid'],
				'customer':     customer['id'],

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
	validate = False,
	auth = False)
def taskModify(request):
	LOG.info(request)
	return jsonrpc.result({'status':'ok'})


@jsonrpc.method(
	validate = V({
		'id':           V(basestring, min=36, max=36),
		'time-destroy':	V(int, default=0),
	}),
	auth = True)
def taskRemove(request):

	if request['time-destroy'] == 0:
		request['time-destroy'] = int(time.time())

	try:
		tasks.remove('id', params['id'], request['time-destroy'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to remove task' })

	return jsonrpc.result({ 'status':'ok' })
