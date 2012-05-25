import copy
import unithelper

from bc.private import rates

class Test(unithelper.TestCase):
	def test_new_metric(self):
		"""Check tariff's rate object"""

		fields = [
			'id',
			'description',
			'mtype', 
			'tariff_id',
			'rate',
			'currency',
			'state',
			'time_create',
			'time_destroy',
			'arg'
		]

		t = rates.Rate()
		self.assertEqual(set(t.values.keys()), set(fields))


	def test_set_rate(self):
		"""Check geting/setting tariff's rate"""

		r = 123L
		c = rates.constants.CURRENCY_USD

		t = rates.Rate()
		t.rate = r
		t.currency = c

		self.assertEqual(t.rate,     r)
		self.assertEqual(t.currency, c)


		with self.assertNotRaises(TypeError):
			t.set({
				'rate':     r,
				'currency': c,
			})


		with self.assertRaises(TypeError):
			t.rate = '123'
			t.currency = c

		with self.assertRaises(TypeError):
			t.rate = 7
