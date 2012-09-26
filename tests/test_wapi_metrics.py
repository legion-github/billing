import uuid

from unithelper import DBTestCase
from unithelper import mocker
from unithelper import requestor
from unithelper import hashable_dict

from bc import database
from bc import metrics

from bc_wapi import wapi_metrics


class Test(DBTestCase):

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
				requestor({'metric': data}, 'ok'))

		self.assertEquals(wapi_metrics.metricGet({'id':''}),
				requestor({'message': 'Metric not found' }, 'error'))

		with mocker([('bc.metrics.get', mocker.exception),
					('bc_wapi.wapi_metrics.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_metrics.metricGet({'id':''}),
				requestor({'message': 'Unable to obtain metric' }, 'servererror'))


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

		self.assertEquals(set(map(lambda x: hashable_dict(x), ans[1]['metrics'])),
				set(map(lambda x: hashable_dict(x), data)))

		with mocker([('bc.metrics.get_all', mocker.exception),
					('bc_wapi.wapi_metrics.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_metrics.metricList({'id':''}),
				requestor({'message': 'Unable to obtain metric list' }, 'servererror'))


	def test_metric_add(self):
		"""Check the creating metric with metricAdd"""

		data={
			'id':         str(uuid.uuid4()),
			'type':       str(uuid.uuid4())[:10],
			'formula':    metrics.constants.FORMULA_SPEED,
			'aggregate':  0L,
		}
		ans = wapi_metrics.metricAdd(data.copy())

		self.assertEquals(ans, requestor({'id':data['id']}, 'ok'))

		with database.DBConnect() as db:
			t1 = db.find('metrics').one()
		self.assertEquals(data['id'], t1['id'])
		self.assertEquals(data['type'], t1['type'])

		with mocker([('bc.metrics.add', mocker.exception),
					('bc_wapi.wapi_metrics.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_metrics.metricAdd({'id':''}),
				requestor({'message': 'Unable to add new metric' }, 'servererror'))

