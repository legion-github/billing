#!/usr/bin/python2.6

import time
import uuid

import readonly
import bobject

from c2 import mongodb

class TariffRateConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'CURRENCY_RUB': 'RUB',
		'CURRENCY_USD': 'USD',
		'CURRENCY_EUR': 'EUR',

		'STATE_ACTIVE':  'active',
		'STATE_ARCHIVE': 'archive',
		'STATE_UPDATE':  'update',
	}

constants = TariffRateConstants()

class TariffRate(bobject.BaseObject):
	def __init__(self, data = None):

		c = TariffRateConstants()

		self.__dict__['values'] = {
			'rid':          str(uuid.uuid4()),
			'description':  '',
			'mtype':        '',
			'tid':          '',
			'rate':         {
				'',
				c.CURRENCY_RUB
			},
			'state':        c.STATE_ACTIVE,
			'time_create':  int(time.time()),
			'time_destroy': 0,
			'arg':          ''
		}

		if data:
			self.set(data)


	def validate(self):
		for n in ['rid', 'mtype', 'tid', 'description']:
			if n not in self.__dict__['values']:
				return False
		return True


	def add(self):
		# XXXlegion: Wrong place for database operations ?
		if not self.validate():
			raise ValueError('Invalid rate')

		mongodb.billing_collection('rates').insert(self.values, safe = True)


def get_by_tariff(tid):
	ret = []
	for o in mongodb.billing_collection('rates').find({ 'tid': tid }):
		ret.append(TariffRate(o))
	return ret


def get_by_id(rid):
	o = mongodb.billing_collection('rates').find_one({ 'rid': rid })
	if o:
		return TariffRate(o)
	return None


def get_by_metric(tid, mtype):
	o = mongodb.billing_collection('rates').find_one(
		{
			'tid':   tid,
			'mtype': mtype
		}
	)
	if o:
		return TariffRate(o)
	return None

