import time
import uuid
import copy

import readonly
import bobject
import rate

from bc import database

class TariffConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'STATE_ENABLE':  'ENABLE',
		'STATE_DISABLE': 'DISABLE'
	}

constants = TariffConstants()

class Tariff(bobject.BaseObject):
	def __init__(self, data = None):

		c = TariffConstants()

		self.__values__ = {
			'create_time': int(time.time()),
			'id':          str(uuid.uuid4()),
			'name':        '',
			'description': '',
			'currency':    rate.constants.CURRENCY_RUB,
			'state':       c.STATE_ENABLE,
		}

		if data:
			self.set(data)


	def get_rates(self):
		""" Gets all tariff's metric rates """

		return rate.get_by_tariff(self.id)


	def export(self):
		""" Exports tariff structure """

		res = copy.deepcopy(self.values)
		res['rates'] = self.get_rates()
		return res


	def set_state(self, state, tid = None):
		""" Change tariffs state """

		tariff_id = (tid or self.id)

		c = TariffConstants()

		if state not in [ c.STATE_ENABLE, c.STATE_DISABLE ]:
			raise ValueError("Unknown state")

		with database.DBConnect() as db:
			db.update('tariffs',
				{'id': tariff_id},
				{'state': state}
				)
		return self


	def create(self, rate_list = None):
		""" Create new tariff """
		with database.DBConnect() as db:
			db.insert('tariffs', self.values)

		if not rate_list:
			return

		for r in rate_list:
			if 'rid' in r:
				del r['rid']
			r['tid'] = self.id

			tr = rate.Rate(r)
			tr.add()

		return self

