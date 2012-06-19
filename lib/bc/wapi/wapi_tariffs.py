__version__ = '1.0'

from bc.validator import Validate as V
from bc import jsonrpc
from bc import log
from bc import tariffs

LOG = log.logger("wapi.tariffs")


@jsonrpc.methods.jsonrpc_method(validate=False, auth=True)
def tariffList(params):
	try:
		ret = map(lambda c: c.values, tariffs.get_all())
	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to obtain tariff list'
			}
		)
	return jsonrpc.methods.jsonrpc_result(
		{
			'status':'ok',
			'tariffs': ret
		}
	)


@jsonrpc.methods.jsonrpc_method(
	validate = V({ 'id': V(basestring, min=36, max=36) }),
	auth = True)
def tariffGet(params):
	try:
		ret = tariffs.get(params['id'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to obtain tariff'
			}
		)
	return jsonrpc.methods.jsonrpc_result(
		{
			'status':'ok',
			'tariff': ret
		}
	)


@jsonrpc.methods.jsonrpc_method(
	validate = V({
		'name':        V(basestring, min=3, max=64),
		'description': V(basestring, min=3, max=1024),
	}),
	auth = True)
def tariffAdd(params):
	try:
		c = tariffs.Tariff(params)
		tariffs.add(c)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to add new tariff'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'status': 'ok' })


@jsonrpc.methods.jsonrpc_method(
	validate = V({
		'id':          V(basestring),
		'name':        V(basestring, min=3, max=64),
		'description': V(basestring, min=3, max=1024),
	}),
	auth = True)
def tariffAddInternal(params):
	try:
		c = tariffs.Tariff(params)
		tariffs.add(c)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to add new tariff'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'status': 'ok' })


@jsonrpc.methods.jsonrpc_method(
	validate = V({
		'id':          V(basestring, min=36, max=36),
		'state':       V(basestring, required=False, max=7),
		'name':        V(basestring, required=False, min=3, max=64),
		'description': V(basestring, required=False, min=3, max=1024),
	}, drop_optional=True),
	auth = True)
def tariffModify(params):
	try:
		if len(params) == 1:
			return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })

		if 'state' in params:
			v = tariffs.constants.import_state(params['state'])
			if v == None or v == tariffs.constants.STATE_DELETED:
				raise TypeError('Wrong state: ' + str(params['state']))
			params['state'] = v

		tariffs.modify('id', params['id'], params)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to modify tariff'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'status': 'ok' })


@jsonrpc.methods.jsonrpc_method(
	validate = V({ 'name': V(basestring, min=3, max=64) }),
	auth = True)
def tariffRemove(params):
	try:
		tariffs.remove('name', params['name'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to remove tariff'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })


@jsonrpc.methods.jsonrpc_method(
	validate = V({ 'id': V(basestring, min=36, max=36) }),
	auth = True)
def tariffIdRemove(params):
	try:
		tariffs.remove('id', params['id'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to remove tariff'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })
