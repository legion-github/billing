__version__ = '1.0'

import bc_jsonrpc as jsonrpc

from bc.validator import Validate as V
from bc import customers
from bc import log
from bc import zones


LOG = log.logger("wapi.customers")


@jsonrpc.method(validate = False, auth = True)
def customerList(request):
	""" Returns a list of all registered customers """

	try:
		ret = map(lambda c: c.values, customers.get_all())

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to obtain customer list' })

	return jsonrpc.result({ 'status':'ok', 'customers': ret })


@jsonrpc.method(
	validate = V({ 'id': V(basestring, min=36, max=36) }),
	auth = True)
def customerGet(params):
	try:
		ret = customers.get(params['id'], 'id')

		if not ret:
			srv = zones.write_zone(params['id'])
			if not srv['local']:
				return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

			return jsonrpc.result_error('InvalidRequest',
				{ 'status': 'error', 'message': 'Customer not found' })

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to obtain customer' })

	return jsonrpc.result({ 'status':'ok', 'customer': ret.values })


@jsonrpc.method(
	validate = V({
		'id':               V(basestring, min=36, max=36),
		'login':            V(basestring, max=64),
		'wallet_mode':      V(basestring, max=7),
		'name_short':       V(basestring, max=255),
		'name_full':        V(basestring, required=False, max=1024),
		'comment':          V(basestring, required=False, max=1024),
		'contact_person':   V(basestring, required=False, min=2, max=255),
		'contact_email':    V(basestring, required=False, max=255),
		'contact_phone':    V(basestring, required=False, max=30),
		'wallet':           V(int       , required=False, min=0),
		'tariff_id':        V(basestring, required=False, min=36, max=36),
		'contract_client':  V(basestring, required=False, max=255),
		'contract_service': V(basestring, required=False, max=255),
	}),
	auth = True)
def customerAdd(params):
	""" Adds new customer account """

	try:
		srv = zones.write_zone(params['id'])
		if not srv['local']:
			return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

		wallet_mode = customers.constants.import_wallet_mode(params['wallet_mode'])

		if wallet_mode == None:
			return jsonrpc.result_error('InvalidRequest', {'status':'error',
				'message':'Wrong wallet_mode: ' + str(params['wallet_mode'])})

		params['wallet_mode'] = wallet_mode

		c = customers.Customer(params)
		customers.add(c)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to add new customer' })

	return jsonrpc.result({ 'status':'ok', 'id':c.id })


@jsonrpc.method(
	validate = V({
		'id':               V(basestring, min=36, max=36),
		'state':            V(basestring, required=False, max=7),
		'wallet_mode':      V(basestring, required=False, max=7),
		'name_short':       V(basestring, required=False, max=255),
		'name_full':        V(basestring, required=False, max=1024),
		'comment':          V(basestring, required=False, max=1024),
		'contact_person':   V(basestring, required=False, min=2, max=255),
		'contact_email':    V(basestring, required=False, max=255),
		'contact_phone':    V(basestring, required=False, max=30),
		'tariff_id':        V(basestring, required=False, min=36, max=36),
		'contract_client':  V(basestring, required=False, max=255),
		'contract_service': V(basestring, required=False, max=255),
	}, drop_optional=True),
	auth = True)
def customerModify(params):
	""" Modify customer's record """

	try:
		srv = zones.write_zone(params['id'])
		if not srv['local']:
			return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

		if len(params) == 1:
			return jsonrpc.result({ 'status':'ok' })

		if 'state' in params:
			v = customers.constants.import_state(params['state'])
			if v == None or v == customers.constants.STATE_DELETED:
				return jsonrpc.result_error('InvalidRequest', {'status':'error',
				'message':'Wrong state: ' + str(params['state'])})
			params['state'] = v

		if 'wallet_mode' in params:
			v = customers.constants.import_wallet_mode(params['wallet_mode'])
			if v == None:
				return jsonrpc.result_error('InvalidRequest', {'status':'error',
				'message':'Wrong wallet_mode: ' + str(params['wallet_mode'])})
			params['wallet_mode'] = v

		customers.modify('id', params['id'], params)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to modify customer' })

	return jsonrpc.result({ 'status':'ok' })


@jsonrpc.method(
	validate = V({ 'id': V(basestring, min=36, max=36) }),
	auth = True)
def customerRemove(params):
	""" Remove customer by name """

	try:
		srv = zones.write_zone(params['id'])
		if not srv['local']:
			return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

		c = customers.remove('id', params['id'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to remove customer' })

	return jsonrpc.result({ 'status':'ok' })


@jsonrpc.method(
	validate = V({
		'id':    V(basestring, min=36, max=36),
		'value': V(int)
	}),
	auth = True)
def customerDeposit(params):
	""" Make deposit to customer """

	try:
		srv = zones.write_zone(params['id'])
		if not srv['local']:
			return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

		if params['value'] != 0:
			customers.deposit(params['id'], params['value'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to make a deposit' })

	return jsonrpc.result({ 'status':'ok' })
