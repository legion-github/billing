import random
import itertools
import uuid
import time

from unithelper import DBTestCase
from unithelper import mocker
from unithelper import requestor
from unithelper import hashable_dict

from bc import database
from bc import rates
from bc import metrics
from bc import tariffs

from bc.wapi import wapi_rates


class Test(DBTestCase):

	def test_rate_get(self):
		"""Check getting rate with rateGet"""

		data = {
			'id':           str(uuid.uuid4()),
			'description':  u'',
			'metric_id':    str(uuid.uuid4()),
			'tariff_id':    str(uuid.uuid4()),
			'rate':         0L,
			'currency':     rates.constants.CURRENCY_RUB,
			'state':        rates.constants.STATE_ACTIVE,
			'time_create':  int(time.time()),
			'time_destroy': 0
		}

		with database.DBConnect() as db:
			db.insert('rates', data)

		self.assertEquals(wapi_rates.rateGet({'id': data['id']}),
				requestor({'rate': data}, 'ok'))

		self.assertEquals(wapi_rates.rateGet({'currency':''}),
				requestor({'message': 'Wrong parameters' }, 'error'))

		self.assertEquals(wapi_rates.rateGet({'currency':'', 'time_destroy':''}),
				requestor({'message': 'Wrong parameters' }, 'error'))

		self.assertEquals(wapi_rates.rateGet({
			'currency':'',
			'time_destroy':'',
			'state':''}),
				requestor({'message': 'Wrong parameters' }, 'error'))

		self.assertEquals(wapi_rates.rateGet({
			'metric_id': data['metric_id'],
			'tariff_id': data['tariff_id'],
			}),
				requestor({'rate': data}, 'ok'))

		self.assertEquals(wapi_rates.rateGet({'id':''}),
				requestor({'message': 'Rate not found' }, 'error'))

		with mocker([('bc.rates.get_by_id', mocker.exception),
					('bc.wapi.wapi_rates.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_rates.rateGet({'id':''}),
				requestor({'message': 'Unable to obtain rate list' }, 'servererror'))


	def test_rate_get_list(self):
		"""Check getting rates with rateList"""

		tariffs_list = [str(uuid.uuid4()) for i in range(5)]
		metrics_list = [str(uuid.uuid4()) for i in range(5)]

		rat = {}
		for tar in tariffs_list:
			rat[tar] = {}
			random.shuffle(metrics_list)
			for met in metrics_list[:random.randint(1, 5)]:

				data = {
					'id':           str(uuid.uuid4()),
					'description':  str(uuid.uuid4()),
					'metric_id':    met,
					'tariff_id':    tar,
					'rate':         random.randint(10**3, 10**10),
					'currency':     rates.constants.CURRENCY_RUB,
					'state':        random.choice([rates.constants.STATE_ACTIVE,
										rates.constants.STATE_DELETED,
										rates.constants.STATE_UPDATE]),
					'time_create':  int(time.time()),
					'time_destroy': 0
					}

				rat[tar][met] = data

				with database.DBConnect() as db:
					db.insert('rates', data)

		list_all = itertools.chain(*[rat[j].itervalues() for j in rat.iterkeys()])

		ans = wapi_rates.rateList('')
		self.assertEquals(ans[0], (01 << 2))
		self.assertEquals(ans[1]['status'], 'ok')

		self.assertEquals(
			set(map(lambda x: hashable_dict(x), ans[1]['rates'])),
			set(map(lambda x: hashable_dict(x),
				filter(lambda x:x['state'] < rates.constants.STATE_DELETED,
					list_all)
				)
			)
		)

		for tar_id in rat.keys():
			ans = wapi_rates.rateList({'tariff_id':tar_id})
			self.assertEquals(ans[0], (01 << 2))
			self.assertEquals(ans[1]['status'], 'ok')

			self.assertEquals(
				set(map(lambda x: hashable_dict(x), ans[1]['rates'])),
				set(map(lambda x: hashable_dict(x),
					filter(lambda x:x['state'] < rates.constants.STATE_DELETED,
						rat[tar_id].values())
					)
				)
			)

		with mocker([('bc.rates.get_all', mocker.exception),
					('bc.wapi.wapi_rates.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_rates.rateList({'id':''}),
				requestor({'message': 'Unable to obtain rate list' }, 'servererror'))


	def test_rate_add(self):
		"""Check the creating rate with rateAdd"""

		data={
				'id':           str(uuid.uuid4()),
				'description':  str(uuid.uuid4()),
				'metric_id':    str(uuid.uuid4()),
				'tariff_id':    str(uuid.uuid4()),
				'rate':         long(random.randint(10**3, 10**10)),
				'currency':     rates.constants.CURRENCY_RUB,
				'state':        rates.constants.STATE_ACTIVE,
				'time_create':  int(time.time()),
				'time_destroy': 0
		}

		tariffs.add(tariffs.Tariff({'id':data['tariff_id']}))

		metrics.add(metrics.Metric({'id':data['metric_id']}))

		self.assertEquals(wapi_rates.rateAdd(data), requestor({}, 'ok'))

		with database.DBConnect() as db:
			t1 = db.find('rates').one()
		self.assertEquals(hashable_dict(data), hashable_dict(t1))

		with mocker([('bc.rates.add', mocker.exception),
					('bc.wapi.wapi_rates.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_rates.rateAdd({'id':''}),
				requestor({'message': 'Unable to add new rate' }, 'servererror'))


	def test_rate_remove(self):
		"""Check state changing with rateRemove"""

		data = {
				'id':           str(uuid.uuid4()),
				'description':  str(uuid.uuid4()),
				'metric_id':    str(uuid.uuid4()),
				'tariff_id':    str(uuid.uuid4()),
				'rate':         long(random.randint(10**3, 10**10)),
				'currency':     rates.constants.CURRENCY_RUB,
				'state':        rates.constants.STATE_ACTIVE,
				'time_create':  int(time.time()),
				'time_destroy': 0
		}

		with database.DBConnect() as db:
			db.insert('rates', data)

		wapi_rates.rateRemove({'id':data['id']})

		data['state'] = rates.constants.STATE_DELETED
		data['time_destroy'] = int(time.time())

		with database.DBConnect() as db:
			t1 = db.find_one('rates', {'id': data['id']})

		self.assertEquals(t1, data)

		with mocker([('bc.rates.remove', mocker.exception),
					('bc.wapi.wapi_rates.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_rates.rateRemove({'id':''}),
				requestor({'message': 'Unable to remove rate' }, 'servererror'))


	def test_rate_modification(self):
		""" Check modification attributes with rateModify"""

		data = {
				'id':           str(uuid.uuid4()),
				'description':  str(uuid.uuid4()),
				'metric_id':    str(uuid.uuid4()),
				'tariff_id':    str(uuid.uuid4()),
				'rate':         long(random.randint(10**3, 10**10)),
				'currency':     rates.constants.CURRENCY_RUB,
				'state':        rates.constants.STATE_ACTIVE,
				'time_create':  int(time.time()),
				'time_destroy': 0
		}

		with database.DBConnect() as db:
			db.insert('rates', data)

		self.assertEqual(wapi_rates.rateModify({'id':data['id']}),
				requestor({}, 'ok'))

		with mocker([('bc.rates.modify', mocker.exception),
					('bc.wapi.wapi_rates.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_rates.rateModify({'id':data['id'], 'rate':10}),
				requestor({'message': 'Unable to modify rate' }, 'servererror'))

		self.assertEqual(
			wapi_rates.rateModify({'id':'w','state':str(rates.constants.STATE_DELETED)}),
			requestor({'message': 'Wrong state: ' + str(rates.constants.STATE_DELETED)}, 'error'))

		self.assertEqual(
			wapi_rates.rateModify({'id':'','currency':str(rates.constants.CURRENCY_USD)}),
			requestor({'message': 'Wrong currency: ' + str(rates.constants.CURRENCY_USD)}, 'error'))

		data1={'id':data['id'], 'description':str(uuid.uuid4())}
		data.update(data1)

		self.assertEqual(wapi_rates.rateModify(data1),
				requestor({}, 'ok'))

		with database.DBConnect() as db:
			t1 = db.find_one('rates', {'id': data['id']})

		self.assertEquals(t1, data)
