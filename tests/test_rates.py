import unithelper
import uuid
import time
import random
import itertools

from bc import rates
from bc import tariffs
from bc import metrics
from bc import database

class Test(unithelper.DBTestCase):
	def test_new_rate(self):
		"""Check tariff's rate object"""

		fields = [
			'id',
			'description',
			'metric_id',
			'tariff_id',
			'rate',
			'currency',
			'state',
			'time_create',
			'time_destroy'
		]

		t = rates.Rate()
		self.assertEqual(set(t.values.keys()), set(fields))


	def test_rates_get(self):
		"""Check getting rate from db"""

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

		rat = rates.Rate(data)

		with database.DBConnect() as db:
			db.insert('rates', data)

		self.assertEquals(rates.get_by_id(rat.id), rat)

		self.assertEquals(rates.get_by_metric(rat.tariff_id, rat.metric_id), rat)


	def test_rates_get_all(self):
		"""Check getting rates from db"""


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

				rat[tar][met] = rates.Rate(data)

				with database.DBConnect() as db:
					db.insert('rates', data)

		list_all = itertools.chain(*[rat[j].itervalues() for j in rat.iterkeys()])
		self.assertEquals(set(list(rates.get_all())),
				set(filter(lambda x: x.state<rates.constants.STATE_DELETED,list_all)))

		for tar_id in rat.keys():
			self.assertEquals(set(list(rates.get_by_tariff(tar_id))),
				set(filter(lambda x: x.state<rates.constants.STATE_DELETED,
							rat[tar_id].values())))


	def test_rates_creation(self):
		"""Check the creating of the rates"""

		rat = rates.Rate(
			{
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
		)

		with self.assertRaises(ValueError):
			rates.add(rat)

		tariffs.add(tariffs.Tariff({'id':rat.tariff_id}))

		with self.assertRaises(ValueError):
			rates.add(rat)

		metrics.add(metrics.Metric({'id':rat.metric_id}))

		rates.add(rat)

		with database.DBConnect() as db:
			r1 = db.find_one('rates', {'id':rat.id})

		self.assertEquals(rates.Rate(r1), rat)


	def test_rate_delete(self):
		"""Check state changing"""

		rat = rates.Rate(
			{
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
		)
		tariffs.add(tariffs.Tariff({'id':rat.tariff_id}))
		metrics.add(metrics.Metric({'id':rat.metric_id}))
		rates.add(rat)

		rat.set({'state': rates.constants.STATE_DELETED,
			'time_destroy': int(time.time())})

		with self.assertRaises(ValueError):
			rates.remove('state', rat.id)

		rates.remove('id', rat.id)

		with database.DBConnect() as db:
			r1 = db.find_one('rates', {'id': rat.id})

		self.assertEquals(rates.Rate(r1), rat)


	def test_rate_modification(self):
		""" Check modification attributes"""

		rat = rates.Rate(
			{
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
		)
		tariffs.add(tariffs.Tariff({'id':rat.tariff_id}))
		metrics.add(metrics.Metric({'id':rat.metric_id}))
		rates.add(rat)

		data = {'description':  str(uuid.uuid4())}
		rates.modify('id', rat.id, data)
		rat.set(data)

		with self.assertRaises(TypeError):
			rates.modify('id', rat.id, {'state':rates.constants.STATE_MAXVALUE+1})

		with self.assertRaises(ValueError):
			rates.modify('name', rat.id, {})

		with database.DBConnect() as db:
			r1 = db.find_one('rates', {'id': rat.id})

		self.assertEquals(rates.Rate(r1), rat)
