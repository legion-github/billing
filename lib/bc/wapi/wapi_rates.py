__version__ = '1.0'

from bc.validator import Validate as V
from bc import jsonrpc
from bc import log
from bc import rates

LOG = log.logger("wapi.rates")


@jsonrpc.methods.jsonrpc_method(
	validate = V({
		'tariff_id': V(basestring, required=False, min=36, max=36),
	}, drop_optional=True),
	auth = True)
def rateList(params):
	try:
		if len(params) == 0:
			ret = map(lambda c: c.values, rates.get_all())

		elif len(params) == 1:
			ret = map(lambda c: c.values, rates.get_by_tariff(parmas['tariff_id']))

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to obtain rate list'
			}
		)
	return jsonrpc.methods.jsonrpc_result(
		{
			'status':'ok',
			'rates': ret
		}
	)


@jsonrpc.methods.jsonrpc_method(
	validate = V({
		'id':        V(basestring, required=False, min=36, max=36),
		'tariff_id': V(basestring, required=False, min=36, max=36),
		'metric_id': V(basestring, required=False, min=1,  max=128),
	}, drop_optional=True),
	auth = True)
def rateGet(params):
	try:
		if len(params) == 1:
			if 'id' not in params:
				return jsonrpc.methods.jsonrpc_result_error('InvalidRequest',
					{
						'status':  'error',
						'message': 'Wrong parameters'
					}
				)
			ret = rates.get_by_id(params['id'])

		elif len(params) == 2:
			if 'tariff_id' not in params or 'metric_id' not in params:
				return jsonrpc.methods.jsonrpc_result_error('InvalidRequest',
					{
						'status':  'error',
						'message': 'Wrong parameters'
					}
				)
			ret = rates.get_by_tariff(params['tariff_id'], params['metric_id'])
		else:
			return jsonrpc.methods.jsonrpc_result_error('InvalidRequest',
				{
					'status':  'error',
					'message': 'Wrong parameters'
				}
			)

		if not ret:
			return jsonrpc.methods.jsonrpc_result_error('InvalidRequest',
				{
					'status':  'error',
					'message': 'Rate not found'
				}
			)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to obtain rate list'
			}
		)
	return jsonrpc.methods.jsonrpc_result(
		{
			'status':'ok',
			'rate': ret.value
		}
	)


@jsonrpc.methods.jsonrpc_method(auth=0)
def rateAdd(params):
	""" Adds new rate """

	try:
		o = rates.Rate(params)
		rates.add(o)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to add new rate'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })


@jsonrpc.methods.jsonrpc_method(
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
			return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })

		if 'state' in params:
			v = rates.constants.import_state(params['state'])
			if v == None or v == rates.constants.STATE_DELETED:
				raise TypeError('Wrong state: ' + str(params['state']))
			params['state'] = v

		if 'currency' in params:
			v = rates.constants.import_currency(params['currency'])
			if v == None:
				raise TypeError('Wrong currency: ' + str(params['currency']))
			params['currency'] = v

		rates.modify('id', params['id'], params)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to modify rate'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })


@jsonrpc.methods.jsonrpc_method(
	validate = V({ 'id': V(basestring, min=36, max=36) }),
	auth = True)
def rateRemove(params):
	try:
		rates.remove('id', params['id'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to remove rate'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })
