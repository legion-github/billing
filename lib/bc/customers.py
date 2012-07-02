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

	def import_state(self, val):
		x = {
			'enable':  self.__readonly__['STATE_ENABLED'],
			'disable': self.__readonly__['STATE_DISABLED'],
			'delete':  self.__readonly__['STATE_DELETED']
		}
		return x.get(val, None)


	def import_wallet_mode(self, val):
		x = {
			'limit':   self.__readonly__['WALLET_MODE_LIMITED'],
			'unlimit': self.__readonly__['WALLET_MODE_UNLIMITED'],
		}
		return x.get(val, None)


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

			'wallet':           0L,
			'wallet_mode':      c.WALLET_MODE_LIMITED
		}

		if data:
			self.set(data)


def get(val, typ='id'):
	"""Finds customer by ID or Login"""

	c = CustomerConstants()

	if typ not in [ 'id', 'login' ]:
		raise ValueError("Unknown type: " + str(typ))

	query = {
		'login': { 'login': val, 'state': c.STATE_ENABLED },
		'id': { 'id': val }
	}

	with database.DBConnect() as db:
		r = db.find_one('customers', query[typ])
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


def modify(typ, val, params):
	"""Modify customer"""

	c = CustomerConstants()

	if typ not in [ 'id', 'login' ]:
		raise ValueError("Unknown type: " + str(typ))

	# Final internal validation
	o = Customer(params)

	if o.state < 0 or o.state >= c.STATE_MAXVALUE:
		raise TypeError('Wrong state')

	if o.wallet_mode < 0 or o.wallet_mode >= c.WALLET_MODE_MAXVALUE:
		raise TypeError('Wrong wallet_mode')

	query = {
		'login': {
			'login': val,
			'$or': [ { 'state': c.STATE_ENABLED }, { 'state': c.STATE_DISABLED } ]
		},
		'id': {
			'id': val
		}
	}

	with database.DBConnect() as db:
		db.update("customers", query[typ], params)


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


def deposit(cid, ammount):
	""" Make deposit to customer """

	with database.DBConnect() as db:
		db.update('customers',
			{ 'id': cid },
			{ '$inc': { 'wallet': ammount } }
		)
