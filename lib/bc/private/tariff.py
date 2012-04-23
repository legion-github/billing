#!/usr/bin/python2.6

import time
import uuid

import readonly

class TariffConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'STATE_ENABLE': 'enable',
		'STATE_DISABLE': 'disable'
	}

constants = TariffConstants()

TARIFF_INFO = {
	'create_time': 0,
	'_id':         '',
	'name':        '',
	'description': '',
	'currency':    '',
	'state': TARIFF_STATE_ENABLE,
}
