__version__ = '1.0'

import bc_jsonrpc as jsonrpc

from bc.validator import Validate as V
from bc import rates
from bc import log

LOG = log.logger("wapi.rates")


@jsonrpc.method(
	validate = V({
		'tariff_id': V(basestring, required=False, min=36, max=36),
	}, drop_optional=True),
	auth = True)
def rateList(params):
	try:
		if len(params) == 0:
			ret = map(lambda c: c.values, rates.get_all())

		elif len(params) == 1:
			ret = map(lambda c: c.values, rates.get_by_tariff(params['tariff_id']))

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to obtain rate list' })

	return jsonrpc.result({ 'status':'ok', 'rates': ret })


@jsonrpc.method(
	validate = V({
		'id':           V(basestring, required=False, min=36, max=36),
		'metric_id':    V(basestring, required=False, min=1,  max=128),
		'tariff_id':    V(basestring, required=False, min=36, max=36),
	}, drop_optional=True),
	auth = True)
def rateGet(params):
	try:
		if len(params) == 1:
			if 'id' not in params:
				return jsonrpc.result_error('InvalidRequest',
					{ 'status': 'error', 'message': 'Wrong parameters' })

			ret = rates.get_by_id(params['id'])

		elif len(params) == 2:
			if 'tariff_id' not in params or 'metric_id' not in params:
				return jsonrpc.result_error('InvalidRequest',
					{ 'status': 'error', 'message': 'Wrong parameters' })

			ret = rates.get_by_metric(params['tariff_id'], params['metric_id'])
		else:
			return jsonrpc.result_error('InvalidRequest',
				{ 'status': 'error', 'message': 'Wrong parameters' })

		if not ret:
			return jsonrpc.result_error('InvalidRequest',
				{ 'status': 'error', 'message': 'Rate not found' })

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to obtain rate list' })

	return jsonrpc.result({ 'status':'ok', 'rate': ret.values })


@jsonrpc.method(
	validate = V({
		'tariff_id':    V(basestring, required=False, min=36, max=36),
		'description':  V(basestring, required=False, min=3,  max=1024),
		'metric_id':    V(basestring, required=False, min=1,  max=128),
		'rate':         V(int,        required=False),
		'currency':     V(basestring, required=False,         max=7),
		'state':        V(basestring, required=False,         max=7),
		'time_create':  V(int,        required=False),
		'time_destroy': V(int,        required=False),
	}, drop_optional=True),
	auth = True)
def rateAdd(params):
	""" Adds new rate """

	try:
		if 'state' in params:
			v = rates.constants.import_state(params['state'])
			if v == None or v == rates.constants.STATE_DELETED:
				return jsonrpc.result_error('InvalidRequest',
						{ 'status': 'error',
							'message':'Wrong state: ' + str(params['state'])})
			params['state'] = v

		if 'currency' in params:
			v = rates.constants.import_currency(params['currency'])
			if v == None:
				return jsonrpc.result_error('InvalidRequest',
						{ 'status': 'error',
							'message':'Wrong currency: ' + str(params['currency'])})
			params['currency'] = v

		o = rates.Rate(params)
		rates.add(o)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to add new rate' })

	return jsonrpc.result({ 'status':'ok', 'id':o.id })


@jsonrpc.method(
	validate = V({
		'id':          V(basestring, min=36, max=36),
		'state':       V(basestring, required=False, max=7),
		'currency':    V(basestring, required=False, min=3, max=3),
		'description': V(basestring, required=False, min=3, max=1024),
	}, drop_optional=True),
	auth = True)
def rateModify(params):
	""" Modify rate """

	try:
		if len(params) == 1:
			return jsonrpc.result({ 'status':'ok' })

		if 'state' in params:
			v = rates.constants.import_state(params['state'])
			if v == None or v == rates.constants.STATE_DELETED:
				return jsonrpc.result_error('InvalidRequest',
						{ 'status': 'error',
							'message':'Wrong state: ' + str(params['state'])})
			params['state'] = v

		if 'currency' in params:
			v = rates.constants.import_currency(params['currency'])
			if v == None:
				return jsonrpc.result_error('InvalidRequest',
						{ 'status': 'error',
							'message':'Wrong currency: ' + str(params['currency'])})
			params['currency'] = v

		rates.modify('id', params['id'], params)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to modify rate' })

	return jsonrpc.result({ 'status':'ok' })


@jsonrpc.method(
	validate = V({ 'id': V(basestring, min=36, max=36) }),
	auth = True)
def rateRemove(params):
	try:
		rates.remove('id', params['id'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to remove rate' })

	return jsonrpc.result({ 'status':'ok' })
