__version__ = '1.0'

import bc_jsonrpc as jsonrpc

from bc.validator import Validate as V
from bc import tariffs
from bc import log
from bc import zones

LOG = log.logger("wapi.tariffs")


@jsonrpc.method(validate=False, auth=True)
def tariffList(params):
	try:
		ret = map(lambda c: c.values, tariffs.get_all())

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to obtain tariff list' })

	return jsonrpc.result({ 'status':'ok', 'tariffs': ret })


@jsonrpc.method(
	validate = V({ 'id': V(basestring, min=36, max=36) }),
	auth = True)
def tariffGet(params):
	try:
		ret = tariffs.get(params['id'])

		if not ret:
			srv = zones.write_zone(params['id'])
			if not srv['local']:
				return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

			return jsonrpc.result_error('InvalidRequest',
				{ 'status': 'error', 'message': 'Tariff not found' })
	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to obtain tariff' })

	return jsonrpc.result({ 'status': 'ok', 'tariff': ret.values })


@jsonrpc.method(
	validate = V({
		'id':          V(basestring, min=36, max=36),
		'name':        V(basestring, min=3, max=64),
		'description': V(basestring, min=3, max=1024),
	}),
	auth = True)
def tariffAdd(params):
	try:
		srv = zones.write_zone(params['id'])
		if not srv['local']:
			return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

		c = tariffs.Tariff(params)
		tariffs.add(c)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to add new tariff' })

	return jsonrpc.result({ 'status': 'ok', 'id':c.id })


@jsonrpc.method(
	validate = V({
		'id':          V(basestring, min=36, max=36),
		'state':       V(basestring, required=False, max=7),
		'name':        V(basestring, required=False, min=3, max=64),
		'description': V(basestring, required=False, min=3, max=1024),
	}, drop_optional=True),
	auth = True)
def tariffModify(params):
	try:
		srv = zones.write_zone(params['id'])
		if not srv['local']:
			return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

		if len(params) == 1:
			return jsonrpc.result({ 'status':'ok' })

		if 'state' in params:
			v = tariffs.constants.import_state(params['state'])
			if v == None or v == tariffs.constants.STATE_DELETED:
				return jsonrpc.result_error('InvalidRequest',
					{ 'status':'error',
						'message':'Wrong state: ' + str(params['state'])})
			params['state'] = v

		tariffs.modify('id', params['id'], params)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to modify tariff' })

	return jsonrpc.result({ 'status': 'ok' })


@jsonrpc.method(
	validate = V({ 'id': V(basestring, min=36, max=36) }),
	auth = True)
def tariffRemove(params):
	try:
		srv = zones.write_zone(params['id'])
		if not srv['local']:
			return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

		tariffs.remove('id', params['id'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to remove tariff' })

	return jsonrpc.result({ 'status':'ok' })
