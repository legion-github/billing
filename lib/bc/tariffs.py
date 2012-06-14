import time
import uuid

from bc import database
from bc import readonly
from bc import bobject


class TariffConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'STATE_ENABLED':  0,
		'STATE_DISABLED': 1,
		'STATE_DELETED':  2,
		'STATE_MAXVALUE': 3,
	}

constants = TariffConstants()

class Tariff(bobject.BaseObject):
	def __init__(self, data = None):

		c = TariffConstants()

		self.__values__ = {
			'id':           unicode(uuid.uuid4()),
			'name':         u'',
			'description':  u'',
			'state':        c.STATE_ENABLED,
			'time_create':  int(time.time()),
			'time_destroy': 0,
		}

		if data:
			self.set(data)


def get(tid):
	""" Finds tariff by ID """

	with database.DBConnect() as db:
		r = db.find_one('tariffs', { 'id': tid })
		if r:
			return Tariff(r)
		return None


def get_all():
	""" Returns all tariffs """

	c = TariffConstants()

	with database.DBConnect() as db:
		for i in db.find('tariffs', { 'state': c.STATE_ENABLED }):
			yield Tariff(i)


def add(obj):
	""" Create new tariff """

	c = TariffConstants()

	with database.DBConnect() as db:
		r = db.find_one('tariffs',
			{
				'name': obj.name,
				'state': c.STATE_ENABLED
			}
		)
		if not r:
			db.insert('tariffs', obj.values)


def remove(typ, value):
	"""Disables tariff"""

	c = TariffConstants()

	if typ == 'id':
		query = { 'id': value }
	elif typ == 'name':
		query = { 'name': value }
	else:
		raise ValueError("Unknown value: " + str(typ))

	with database.DBConnect() as db:
		db.update("customers", query,
			{
				'state': c.STATE_DELETED,
				'time_destroy': int(time.time())
			}
		)
