#!/usr/bin/python2.6

import time
import uuid

import bobject
import readonly

from bc import database

class CustomerConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'STATE_ENABLED':  0,
		'STATE_DISABLED': 1,
		'STATE_DELETED':  2,
		'STATE_MAXVALUE': 3,

		'WALLET_MODE_LIMITED':   0,
		'WALLET_MODE_UNLIMITED': 1,
		'WALLET_MODE_MAXVALUE':  2,
	}

constants = CustomerConstants()

class Customer(bobject.BaseObject):
	def __init__(self, data = None):

		c = CustomerConstants()

		self.__values__ = {
			'id': str(uuid.uuid4()),

			'login':            u'',

			'name_short':       u'',
			'name_full':        u'',

			'comment':          u'',

			'contract_client':  u'',
			'contract_service': u'',

			'tariff_id':        u'',

			'contact_person':   u'',
			'contact_email':    u'',
			'contact_phone':    u'',

			'state':            c.STATE_ENABLED,

			'time_create':      int(time.time()),
			'time_destroy':     0,

			'wallet':           0,
			'wallet_mode':      c.WALLET_MODE_LIMITED
		}

		if data:
			self.set(data)


def get(cid):
	"""Finds customer by ID"""

	with database.DBConnect() as db:
		r = db.find_one('customers', { 'id': cid })
		if r:
			return Customer(r)
		return None


def get_all():
	"""Returns all not deleted customers"""

	with database.DBConnect() as db:
		c = CustomerConstants()
		for i in db.find('customers', { 'state': c.STATE_ENABLED }):
			yield Customer(i)


def add(obj):
	"""Creates new customer"""

	c = CustomerConstants()

	if obj.state < 0 or obj.state >= c.STATE_MAXVALUE:
		raise TypeError('Wrong state')

	if obj.wallet_mode < 0 or obj.wallet_mode >= c.WALLET_MODE_MAXVALUE:
		raise TypeError('Wrong wallet_mode')

	with database.DBConnect() as db:
		r = db.find_one('customers',
			{
				'login': obj.login,
				'state': c.STATE_ENABLED
			}
		)
		if not r:
			db.insert('customers', obj.values)


def remove(typ, value):
	"""Disables customer"""

	if typ == 'id':
		query = { 'id': value }
	elif typ == 'login':
		query = { 'login': value }
	else:
		raise ValueError("Unknown value: " + str(typ))

	with database.DBConnect() as db:
		c = CustomerConstants()
		db.update("customers", query,
			{
				'state': c.STATE_DELETED,
				'time_destroy': int(time.time())
			}
		)
