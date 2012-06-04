#!/usr/bin/python2.6

import time
import uuid

from bc import database

from bc.private import readonly
from bc.private import bobject

class RateConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'CURRENCY_RUB': 'RUB',
		'CURRENCY_USD': 'USD',
		'CURRENCY_EUR': 'EUR',

		'STATE_ACTIVE':  'active',
		'STATE_ARCHIVE': 'archive',
		'STATE_UPDATE':  'update',
	}

constants = RateConstants()

class Rate(bobject.BaseObject):
	def __init__(self, data = None):

		c = RateConstants()

		self.__values__ = {
			'id':           str(uuid.uuid4()),
			'description':  '',
			'mtype':        '',
			'tariff_id':    '',
			'arg':          '',
			'rate':         0L,
			'currency':     c.CURRENCY_RUB,
			'state':        c.STATE_ACTIVE,
			'time_create':  int(time.time()),
			'time_destroy': 0
		}

		if data:
			self.set(data)


def add(rate):
	with database.DBConnect() as db:
		r = db.find_one('rates', { 'id': rate.id }, fields=['id'])
		if not r:
			db.insert('rates', rate.values)


def get_by_tariff(tid):
	with database.DBConnect() as db:
		for o in db.find('rates', { 'tariff_id': tid }):
			yield Rate(o)


def get_by_id(rid):
	with database.DBConnect() as db:
		o = db.find_one('rates', { 'id': rid })
		if o:
			return Rate(o)
		return None


def get_by_metric(tid, mtype):
	with database.DBConnect() as db:
		o = db.find_one('rates', { 'tariff_id': tid, 'mtype': mtype })
		if o:
			return Rate(o)
		return None
