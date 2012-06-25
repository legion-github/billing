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
			'type':		V(basestring),
			'customer':	V(basestring, min=36, max=36, default=None),
			'uuid':		V(basestring, min=36, max=36),
			'user':		V(basestring, min=1,  max=64),
			'value':	V(int),
			'descr':	V(basestring),
			'time-create':	V(int),
			'time-destroy':	V(int, default=0),
	}),
	auth = False)
def taskAdd(request):
	""" Open new billing task """

	if 'time-create' not in request:
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
				'customer':     customer['_id'],

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
	validate = False,
	auth = True)
def taskRemove(request):
	LOG.info(request)
	return jsonrpc.result({'status':'ok'})

