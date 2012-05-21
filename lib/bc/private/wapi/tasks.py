#!/usr/bin/paython

__version__ = '1.0'

from billing import customers

from bc.private   import queue
from bc.private   import tasks
from bc.validator import Validate as V
from bc           import jsonrpc
from bc           import log

LOG = log.logger("wapi.tasks")

@jsonrpc.methods.jsonrpc_method(
	validate = V({
			'type':		V(basestring),
			'customer':	V(basestring, min=36, max=36, default=None),
			'uuid':		V(basestring, min=36, max=36),
			'user':		V(basestring, min=1,  max=64),
			'value':	V(int),
			'descr':	V(basestring),
			'arg':		V(basestring),
			'time-create':	V(int),
			'time-destroy':	V(int, default=0),
	}),
	auth = False)
def taskOpen(environ, request):
	""" Open new billing task """

	if 'time-create' not in request:
		request['time-create'] = int(time.time())

	# Temp hack for now
	#if not request['customer']:
	#	res = mongodb.collection('log_accounts').find_one(
	#		{ 'user': request['user'] }
	#	)
	#	if not res:
	#		LOG.error("Unable to find customer by user: %s", request['user'])
	#		return jsonrpc.methods.jsonrpc_result({'status':'fail'})
	#
	#	request['customer'] = res['customer']

	customer = customers.get(request['customer'], ignore_wallets = True)
	rid, rate  = queue.resolve(request['type'], customer['tariff'], request['arg'])

	if not rid:
		return jsonrpc.methods.jsonrpc_result({'status':'fail'})

	try:
		t = task.Task()
		t.set({
			'uuid':         request['uuid'],
			'customer':     customer['_id'],

			'time_create':  request['time-create'],
			'time_check':   request['time-create'],
			'time_destroy': request['time-destroy'],

			'target_user':  request['user'],
			'target_uuid':  request['uuid'],
			'target_descr': request['descr'],
		})

		queue.task_add(request['type'], t)

	except Exception, e:
		LOG.exception("Unable to add new task: %s", e)
		return jsonrpc.methods.jsonrpc_result({'status':'fail'})

	return jsonrpc.methods.jsonrpc_result({'status':'ok'})


@jsonrpc.methods.jsonrpc_method(
	validate = False,
	auth = False)
def taskReopen(request):
	LOG.info(request)
	return jsonrpc.methods.jsonrpc_result({'status':'ok'})


@jsonrpc.methods.jsonrpc_method(
	validate = False,
	auth = True)
def taskClose(request):
	LOG.info(request)
	return jsonrpc.methods.jsonrpc_result({'status':'ok'})

