import unithelper
import uuid

from bc import database
from bc import metrics

from bc.wapi import wapi_metrics


class Test(unithelper.DBTestCase):

	def test_metric_get(self):
		"""Check getting metric with metricGet"""

		data={
				'id':         str(uuid.uuid4()),
				'type':       str(uuid.uuid4())[:10],
				'formula':    metrics.constants.FORMULA_SPEED,
				'aggregate':  0L,
			}

		with database.DBConnect() as db:
			db.insert('metrics', data)

		self.assertEquals(wapi_metrics.metricGet({'id': data['id']}),
				unithelper.requestor({'metric': data}, 'ok'))

		self.assertEquals(wapi_metrics.metricGet({'id':''}),
				unithelper.requestor({'message': 'Metric not found' }, 'error'))

		with unithelper.mocker('bc.metrics', 'get', 'bc.wapi.wapi_metrics'):
			self.assertEquals(wapi_metrics.metricGet({'id':''}),
				unithelper.requestor({'message': 'Unable to obtain metric' }, 'servererror'))


	def test_metric_get_list(self):
		"""Check getting metrics with metricList"""

		data = []
		for i in range(2, 10):
			d={
				'id':         str(uuid.uuid4()),
				'type':       str(uuid.uuid4())[:10],
				'formula':    metrics.constants.FORMULA_SPEED,
				'aggregate':  0L,
			}

			with database.DBConnect() as db:
				db.insert('metrics', d)

			data.append(d)

		ans = wapi_metrics.metricList('')
		self.assertEquals(ans[0], (01 << 2))
		self.assertEquals(ans[1]['status'], 'ok')

		self.assertEquals(set(map(lambda x: unithelper.hashable_dict(x), ans[1]['metrics'])),
				set(map(lambda x: unithelper.hashable_dict(x), data)))

		with unithelper.mocker('bc.metrics', 'get_all', 'bc.wapi.wapi_metrics'):
			self.assertEquals(wapi_metrics.metricList({'id':''}),
				unithelper.requestor({'message': 'Unable to obtain metric list' }, 'servererror'))


	def test_metric_add(self):
		"""Check the creating metric with metricAdd"""

		data={
			'id':         str(uuid.uuid4()),
			'type':       str(uuid.uuid4())[:10],
			'formula':    metrics.constants.FORMULA_SPEED,
			'aggregate':  0L,
		}
		ans = wapi_metrics.metricAdd(data)

		self.assertEquals(ans, unithelper.requestor({}, 'ok'))

		with database.DBConnect() as db:
			t1 = db.find('metrics').one()
		self.assertEquals(data['id'], t1['id'])
		self.assertEquals(data['type'], t1['type'])

		with unithelper.mocker('bc.metrics', 'add', 'bc.wapi.wapi_metrics'):
			self.assertEquals(wapi_metrics.metricAdd({'id':''}),
				unithelper.requestor({'message': 'Unable to add new metric' }, 'servererror'))

