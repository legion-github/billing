import uuid
import unithelper

from bc import metrics
from bc import database

class Test(unithelper.DBTestCase):

	def test_new_metric(self):
		"""Check metric creation"""

		values = {
			'id':         u'',
			'type':       u'',
			'formula':    u'',
			'aggregate':  0L,
		}

		t = metrics.Metric()
		self.assertEqual(set(t.values.keys()), set(values.keys()))


	def test_metric_creation(self):
		"""Check the creating of the metric"""

		met = metrics.Metric(
			data={
				'id':         str(uuid.uuid4()),
				'type':       str(uuid.uuid4())[:10],
				'formula':    metrics.constants.FORMULA_SPEED,
				'aggregate':  0L,
			}
		)
		metrics.add(met)

		with database.DBConnect() as db:
			m1 = db.find_one('metrics', {'id':met.id})

		self.assertEquals(metrics.Metric(m1), met)


	def test_metric_get(self):
		"""Check getting metric from db"""

		data = {
				'id':         str(uuid.uuid4()),
				'type':       str(uuid.uuid4())[:10],
				'formula':    metrics.constants.FORMULA_SPEED,
				'aggregate':  0L,
		}

		met = metrics.Metric(data)

		with database.DBConnect() as db:
			db.insert('metrics', data)

		self.assertEquals(metrics.get(met.id), met)


	def test_metric_get_all(self):
		"""Check getting metrics from db"""

		data = {
				'id':         str(uuid.uuid4()),
				'type':       str(uuid.uuid4())[:10],
				'formula':    metrics.constants.FORMULA_UNIT,
				'aggregate':  0L,
		}
		data1 = data.copy()
		data1['id'] = unicode(uuid.uuid4())
		data1['formula'] = metrics.constants.FORMULA_TIME

		met = metrics.Metric(data)
		met1 = metrics.Metric(data1)

		with database.DBConnect() as db:
			db.insert('metrics', data)
			db.insert('metrics', data1)

		#TODO nekolyanich: more syntax nice check
		all=list(metrics.get_all())
		self.assertTrue(met in all)
		self.assertTrue(met1 in all)
		self.assertTrue(all[0] in [met, met1])
		self.assertTrue(all[1] in [met, met1])

