#
# wapi_rates.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
# Copyright (c) 2012-2013 by Nikolay Ivanov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#
__version__ = '1.0'

import bc_jsonrpc as jsonrpc

from bc.validator import Validate as V
from bc import rates
from bc import log
from bc import zones

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
		'metric_id':    V(basestring, required=True, min=1,  max=128),
		'tariff_id':    V(basestring, required=True, min=36, max=36),
	}),
	auth = True)
def rateGet(params):
	try:
		ret = rates.get_by_metric(params['tariff_id'], params['metric_id'])
		if not ret:
			srv = zones.write_zone(params['tariff_id'])
			if not srv['local']:
				return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

			return jsonrpc.result_error('InvalidRequest',
				{ 'status': 'error', 'message': 'Rate not found' })

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to obtain rate list' })

	return jsonrpc.result({ 'status':'ok', 'rate': ret.values })


@jsonrpc.method(
	validate = V({
		'metric_id':    V(basestring, required=False, min=1,  max=128),
		'tariff_id':    V(basestring, required=False, min=36, max=36),
		'description':  V(basestring, required=False, min=3,  max=1024),
		'rate':         V(int,        required=False),
		'currency':     V(basestring, required=False,         max=7),
		'state':        V(basestring, required=False,         max=7),
	}, drop_optional=True),
	auth = True)
def rateAdd(params):
	""" Adds new rate """

	try:
		srv = zones.write_zone(params['tariff_id'])
		if not srv['local']:
			return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

		if 'currency' in params:
			v = rates.constants.import_currency(params['currency'])
			w = rates.constants.import_state(params['state'])
			if v == None:
				return jsonrpc.result_error('InvalidRequest',
						{ 'status': 'error',
							'message':'Wrong currency: ' + str(params['currency'])})
			if w == None:
				return jsonrpc.result_error('InvalidRequest',
						{ 'status': 'error',
							'message':'Wrong state: ' + str(params['state'])})
			params['currency'] = v
			params['state'] = w

		o = rates.Rate(params)
		rates.add(o)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to add new rate' })

	return jsonrpc.result({ 'status':'ok', 'id':o.id })


@jsonrpc.method(
	validate = V({
		'metric_id':   V(basestring, min=1,  max=128),
		'tariff_id':   V(basestring, min=36, max=36),
		'currency':    V(basestring, required=False, min=3, max=3),
		'description': V(basestring, required=False, min=3, max=1024),
	}, drop_optional=True),
	auth = True)
def rateModify(params):
	""" Modify rate """

	try:
		srv = zones.write_zone(params['tariff_id'])
		if not srv['local']:
			return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

		if len(params) <= 2:
			return jsonrpc.result_error('InvalidRequest',
					{ 'status': 'error',
					  'message':'More arguments required' })

		if 'currency' in params:
			v = rates.constants.import_currency(params['currency'])
			if v == None:
				return jsonrpc.result_error('InvalidRequest',
						{ 'status': 'error',
						  'message':'Wrong currency: ' + str(params['currency'])})
			params['currency'] = v

		tid, mid = params['tariff_id'], params['metric_id']
		del params['tariff_id'], params['metric_id']

		rates.modify(tid, mid, params)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to modify rate' })

	return jsonrpc.result({ 'status':'ok' })


@jsonrpc.method(
	validate = V({ 
		'metric_id':   V(basestring, min=1,  max=128),
		'tariff_id':   V(basestring, min=36, max=36),
	}),
	auth = True)
def rateRemove(params):
	try:
		srv = zones.write_zone(params['tariff_id'])
		if not srv['local']:
			return jsonrpc.result({ 'status':'redirect', 'server': srv['server'] })

		rates.remove(params['tariff_id'], params['metric_id'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.result_error('ServerError',
			{ 'status': 'error', 'message': 'Unable to remove rate' })

	return jsonrpc.result({ 'status':'ok' })
