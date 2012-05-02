import copy
import unithelper

from bc.private.rate import Rate
from bc.private import tariff_rate

class Test(unithelper.TestCase):
	def test_new_metric(self):
		"""Check tariff's rate object"""

		fields = [
			'rid',
			'description',
			'mtype', 
			'tid',
			'rate',
			'state',
			'time_create',
			'time_destroy',
			'arg'
		]

		t = tariff_rate.TariffRate()
		self.assertEqual(set(t.values.keys()), set(fields))


	def test_set_rate(self):
		"""Check geting/setting tariff's rate"""

		r = Rate(1)
		c = tariff_rate.constants.CURRENCY_USD

		t = tariff_rate.TariffRate()
		t.rate = {
			'value':    r,
			'currency': c,
		}

		self.assertEqual(str(t.rate['value']),    str(r))
		self.assertEqual(str(t.rate['currency']), str(c))


		with self.assertNotRaises(TypeError):
			t.set({
				'rate': {
					'value':    r,
					'currency': c,
				}
			})

		with self.assertRaises(TypeError):
			t.rate = {
				'value':    r,
			}

		with self.assertRaises(TypeError):
			t.rate = {
				'value':    '123',
				'currency': c,
			}

		with self.assertRaises(TypeError):
			t.rate = 7
