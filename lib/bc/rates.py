#!/usr/bin/python2.6

import time
import uuid

from bc import database
from bc import readonly
from bc import bobject

from bc import tariffs
from bc import metrics

class RateConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'CURRENCY_RUB': 1,
		'CURRENCY_USD': 2,
		'CURRENCY_EUR': 3,

		'STATE_ACTIVE':   0,
		'STATE_UPDATE':   1,
		'STATE_DELETED':  2,
		'STATE_MAXVALUE': 3,
	}

	def import_state(self, val):
		switch = {
			'active': self.__readonly__['STATE_ACTIVE'],
			'update': self.__readonly__['STATE_UPDATE'],
			'delete': self.__readonly__['STATE_DELETED']
		}
		return switch.get(val.lower(), None)

	def import_currency(self, val):
		switch = {
			'rub': self.__readonly__['CURRENCY_RUB'],
			'usd': self.__readonly__['CURRENCY_USD'],
			'eur': self.__readonly__['CURRENCY_EUR']
		}
		return switch.get(val.lower(), None)


constants = RateConstants()

class Rate(bobject.BaseObject):
	def __init__(self, data = None):

		c = RateConstants()

		self.__values__ = {
			'id':           str(uuid.uuid4()),
			'description':  u'',
			'metric_id':    u'',
			'tariff_id':    u'',
			'rate':         0L,
			'currency':     c.CURRENCY_RUB,
			'state':        c.STATE_ACTIVE,
			'time_create':  int(time.time()),
			'time_destroy': 0
		}

		if data:
			if 'sync' in data:
				del data['sync']
			self.set(data)


def add(obj):
	"""Creates new metrics rate for tariff"""

	c = RateConstants()

	if obj.state < 0 or obj.state >= c.STATE_MAXVALUE:
		raise TypeError('Wrong state')

	with database.DBConnect() as db:
		r = tariffs.get(obj.tariff_id)
		if not r:
			raise ValueError("Wrong tariff")

		r = metrics.get(obj.metric_id)
		if not r:
			raise ValueError("Wrong metric")

		r = db.find_one('rates', { 'id': obj.id }, fields=['id'])
		if not r:
			db.insert('rates', obj.values)


def remove(tid, mid):
	"""Disables rate"""

	c = RateConstants()

	with database.DBConnect() as db:
		r = db.find_one('rates', 
			{
				'tariff_id': tid,
				'metric_id': mid
			},
			fields=['state']
		)

		if not r:
			raise ValueError("Wrong rate")

		if r['state'] != c.STATE_ACTIVE:
			raise ValueError("Rate busy")

		db.update("rates",
			{
				'tariff_id': tid,
				'metric_id': mid,
				'state':     c.STATE_ACTIVE
			},
			{
				'state': c.STATE_DELETED,
				'time_destroy': int(time.time()),
				'sync': 0
			}
		)


def modify(tid, mid, params):
	"""Modify rate"""

	c = RateConstants()

	params['sync'] = 0

	with database.DBConnect() as db:
		db.update("rates",
			{
				'tariff_id': tid,
				'metric_id': mid
			},
			params
		)


def get_all():
	c = RateConstants()

	with database.DBConnect() as db:
		for o in db.find('rates', { 'state': { '$lt': c.STATE_DELETED }}):
			yield Rate(o)


def get_by_tariff(tid):
	c = RateConstants()

	with database.DBConnect() as db:
		for o in db.find('rates', { 'tariff_id': tid, 'state': { '$lt': c.STATE_DELETED }}):
			yield Rate(o)


def get_by_metric(tid, mid):
	with database.DBConnect() as db:
		o = db.find_one('rates', { 'tariff_id': tid, 'metric_id': mid })
		if o:
			return Rate(o)
		return None


def resolve(mid, tid):
	"""Rate information by tariff and metric"""

	c = RateConstants()

	with database.DBConnect() as db:
		r = db.find_one('rates',
			{
				'state':     c.STATE_ACTIVE,
				'metric_id': mid,
				'$or': [
					{ 'tariff_id': tid },
					{ 'tariff_id': '*' }
				]
			},
			fields=[ 'id', 'rate' ]
		)
		if not r:
			return (None, None)
		return (r['id'], r['rate'])
