#!/usr/bin/paython

__version__ = '1.0'

import uuid, logging

from billing import customers

from bc.private   import queue
from bc.private   import task
from bc.validator import Validate as V
from bc           import jsonrpc

from c2 import mongodb

LOG = logging.getLogger("c2.abc")

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

	# Temp hack for now
	customer = request.get('customer')
	if not customer:
		user_id = request.get('user')
		res = mongodb.billing_collection('log_accounts').find_one({'user': user_id})
		if not res:
			logging.getLogger("c2.billing").error("Unable to find customer by user: %s", str(user_id))
			return jsonrpc.methods.jsonrpc_result({'status':'fail'})
		request['customer'] = res['customer']

	customer = customers.get(request.get('customer'), ignore_wallets = True)
	now = int(time.time())

	t = task.Task()
	rid, rate  = queue.resolve(request.get('type'), customer['tariff'], request.get('arg'))

	if not rid:
		return jsonrpc.methods.jsonrpc_result({'status':'fail'})

	t.uuid         = request.get('uuid')
	t.customer     = customer['_id']

	t.time_create  = request.get('time-create', now)
	t.time_check   = request.get('time-create', now)
	t.time_destroy = request.get('time-destroy', 0)

	t.target_user  = request.get('user')
	t.target_uuid  = request.get('uuid')
	t.target_descr = request.get('descr')

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

