#!/usr/bin/python2.6

import time
import uuid

import readonly
import bobject

from rate import Rate

from c2 import mongodb

class TariffRateConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		CURRENCY_RUB: 'RUB',
		CURRENCY_USD: 'USD',
		CURRENCY_EUR: 'EUR',

		STATE_ACTIVE:  'active',
		STATE_ARCHIVE: 'archive',
		STATE_UPDATE:  'update',
	}

constants = TariffRateConstants()

class TariffRate(bobject.BaseObject):
	def __init__(self, tariff_id = None, mtype = None):

		c = TariffRateConstants()

		self.__dict__['values'] = {
			'rid':          '',
			'description':  '',
			'mtype':        '',
			'tariff_id':    '',
			'rate':         { Rate(0), c.CURRENCY_RUB },
			'state':        c.STATE_ACTIVE,
			'time_create':  int(time.time()),
			'time_destroy': 0,
			'arg':          ''
		}

		if not mtype:
			return

		o = mongodb.billing_collection('rates').find_one(
			{
				'mtype':     mtype,
				'tariff_id': tariff_id,
			}
		)
		if not o:
			raise ValueError('Unknown rate')
		self.set(o)


	def validate(self):
		for n in ['rid', 'mtype', 'tariff_id', 'description']:
			if n not in self.__dict__['values']:
				return False
		return True


	def add(self):
		# XXXlegion: Wrong place for database operations ?
		if not self.validate():
			raise ValueError('Invalid rate')

		mongodb.billing_collection('rates').insert(self.values, safe = True)

