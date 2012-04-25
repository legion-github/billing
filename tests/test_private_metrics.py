import copy
import unittest
from bc.private import metrics

class Test(unittest.TestCase):
	def test_new_metric(self):
		"""Check metric creation"""

		values = {
			'mtype':           '',
			'count_dimention': {},
			'time_dimention':  {},
			'time_type':       0,
			'aggrigate':       0,
		}

		t = metrics.Metric()
		self.assertEqual(set(t.values.keys()), set(values.keys()))


	def test_change_metric(self):
		"""Check metric modification"""

		t = metrics.Metric()

		def setx():
			t.mtype = 123
		self.assertRaises(TypeError, setx)

		def setx():
			t.zzz = 1
		self.assertRaises(KeyError, setx)

		def setx():
			del t.zzz
		self.assertRaises(ValueError, setx)

		def setx():
			t.mtype = '123'
		self.assertTrue(setx)


	def test_export_metric(self):
		"""Check metric exporting"""

		m = metrics.Metric()
		r1 = copy.deepcopy(m.values)
		m.mtype = '123'
		r2 = copy.deepcopy(m.values)

		self.assertEqual(r1['mtype'], '')
		self.assertEqual(r2['mtype'], '123')

		m = metrics.Metric()
		r1 = copy.deepcopy(m.values)
		m.set({'mtype':'123'})
		r2 = copy.deepcopy(m.values)

		self.assertEqual(r1['mtype'], '')
		self.assertEqual(r2['mtype'], '123')

