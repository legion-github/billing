import time
import uuid

import readonly
import bobject
import tariff_rate

from c2 import mongodb

class TariffConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'STATE_ENABLE':  'enable',
		'STATE_DISABLE': 'disable'
	}

constants = TariffConstants()

class Tariff(bobject.BaseObject):
	def __init__(self, data = None):

		c = TariffConstants()

		self.__dict__['values'] = {
			'create_time': int(time.time()),
			'_id':         str(uuid.uuid4()),
			'name':        '',
			'description': '',
			'currency':    tariff_rate.constants.CURRENCY_RUB,
			'state':       c.STATE_ENABLE,
		}

		if data:
			self.set(data)


	def get_rates(self):
		""" Gets all tariff's metric rates """

		return tariff_rate.get_by_tariff(self._id)


	def export(self):
		""" Exports tariff structure """

		res = copy.deepcopy(self.values)
		res['rates'] = self.get_rates()
		return res


	def set_state(self, state, tid = None):
		""" Change tariffs state """

		tariff_id = (tid or self._id)

		c = TariffConstants()

		if state not in [ c.STATE_ENABLE, c.STATE_DISABLE ]:
			raise ValueError("Unknown state")

		mongodb.billing_collection('tariffs').update(
			{
				'_id':   tariff_id,
				'state': state,
			}
		)
		return self


	def create(self, rate_list = None):
		""" Create new tariff """

		mongodb.billing_collection('tariffs').insert(self.values, safe=True)

		if not rate_list:
			return

		for r in rate_list:
			if 'rid' in r:
				del r['rid']
			r['tid'] = self._id

			tr = tariff_rate.TariffRate(r)
			tr.add()

		return self

