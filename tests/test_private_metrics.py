import copy
import unithelper
from bc.private import metrics

class Test(unithelper.TestCase):
	def test_new_metric(self):
		"""Check metric creation"""

		values = {
			'mtype':           '',
			'count_dimention': {},
			'time_dimention':  {},
			'time_type':       0,
			'aggregate':       0,
		}

		t = metrics.Metric()
		self.assertEqual(set(t.values.keys()), set(values.keys()))


	def test_change_metric(self):
		"""Check metric modification"""

		t = metrics.Metric()

		with self.assertRaises(TypeError):
			t.mtype = 123

		with self.assertRaises(KeyError):
			t.zzz = 1

		with self.assertRaises(ValueError):
			del t.zzz

		with self.assertNotRaises(TypeError):
			t.mtype = '123'


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


def test_add_metric(self):
	"""Check metric add"""


