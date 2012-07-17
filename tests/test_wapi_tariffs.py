import unithelper
import uuid
import time

from bc import database
from bc import tariffs

from bc.wapi import wapi_tariffs


class Test(unithelper.DBTestCase):

	def test_tariff_get(self):
		"""Check getting tariff with tariffGet"""

		data = {
			'id':           unicode(uuid.uuid4()),
			'name':         str(uuid.uuid4()),
			'description':  str(uuid.uuid4()),
			'state':        tariffs.constants.STATE_ENABLED,
			'time_create':  int(time.time()),
			'time_destroy': 0,
		}

		with database.DBConnect() as db:
			db.insert('tariffs', data)

		self.assertEquals(wapi_tariffs.tariffGet({'id': data['id']}),
				unithelper.requestor({'tariff': data}, 'ok'))

		self.assertEquals(wapi_tariffs.tariffGet({'id':''}),
				unithelper.requestor({'message': 'Tariff not found' }, 'error'))

		with unithelper.mocker('bc.tariffs', 'get', 'bc.wapi.wapi_tariffs'):
			self.assertEquals(wapi_tariffs.tariffGet({'id':''}),
				unithelper.requestor({'message': 'Unable to obtain tariff' }, 'servererror'))


	def test_tariff_get_list(self):
		"""Check getting tariffs with tariffList"""

		data = []
		for i in range(2, 10):
			d = {
				'id':           unicode(uuid.uuid4()),
				'name':         str(uuid.uuid4()),
				'description':  str(uuid.uuid4()),
				'state':        tariffs.constants.STATE_ENABLED,
				'time_create':  int(time.time()),
				'time_destroy': 0,
			}

			with database.DBConnect() as db:
				db.insert('tariffs', d)

			data.append(d)

		ans = wapi_tariffs.tariffList('')
		self.assertEquals(ans[0], (01 << 2))
		self.assertEquals(ans[1]['status'], 'ok')

		self.assertEquals(set(map(lambda x: unithelper.hashable_dict(x), ans[1]['tariffs'])),
				set(map(lambda x: unithelper.hashable_dict(x), data)))

		with unithelper.mocker('bc.tariffs', 'get_all', 'bc.wapi.wapi_tariffs'):
			self.assertEquals(wapi_tariffs.tariffList({'id':''}),
				unithelper.requestor({'message': 'Unable to obtain tariff list' }, 'servererror'))


	def test_tariff_add(self):
		"""Check the creating tariff with taeriffAdd"""

		data={
			'name': str(uuid.uuid4()),
			'description': str(uuid.uuid4()),
		}
		ans = wapi_tariffs.tariffAdd(data)

		self.assertEquals(ans, unithelper.requestor({}, 'ok'))

		with database.DBConnect() as db:
			t1 = db.find('tariffs').one()
		self.assertEquals(data['name'], t1['name'])
		self.assertEquals(data['description'], t1['description'])

		with unithelper.mocker('bc.tariffs', 'add', 'bc.wapi.wapi_tariffs'):
			self.assertEquals(wapi_tariffs.tariffAdd({'id':''}),
				unithelper.requestor({'message': 'Unable to add new tariff' }, 'servererror'))


	def test_tariff_add_internal(self):
		"""Check the creating tariff with taeriffAddInternal"""

		data={
			'id': str(uuid.uuid4()),
			'name': str(uuid.uuid4()),
			'description': str(uuid.uuid4()),
		}
		ans = wapi_tariffs.tariffAdd(data)

		self.assertEquals(ans, unithelper.requestor({}, 'ok'))

		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'id': data['id']})
		self.assertEquals(data['name'], t1['name'])
		self.assertEquals(data['description'], t1['description'])

		with unithelper.mocker('bc.tariffs', 'add', 'bc.wapi.wapi_tariffs'):
			self.assertEquals(wapi_tariffs.tariffAdd({'id':''}),
				unithelper.requestor({'message': 'Unable to add new tariff' }, 'servererror'))


	def test_tariff_id_remove(self):
		"""Check state changing with tariffIdRemove"""

		data = {
			'id':           unicode(uuid.uuid4()),
			'name':         str(uuid.uuid4()),
			'description':  str(uuid.uuid4()),
			'state':        tariffs.constants.STATE_ENABLED,
			'time_create':  int(time.time()),
			'time_destroy': 0,
		}

		with database.DBConnect() as db:
			db.insert('tariffs', data)

		wapi_tariffs.tariffIdRemove({'id':data['id']})

		data['state'] = tariffs.constants.STATE_DELETED
		data['time_destroy'] = int(time.time())

		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'id': data['id']})

		self.assertEquals(t1, data)

		with unithelper.mocker('bc.tariffs', 'remove', 'bc.wapi.wapi_tariffs'):
			self.assertEquals(wapi_tariffs.tariffIdRemove({'id':''}),
				unithelper.requestor({'message': 'Unable to remove tariff' }, 'servererror'))


	def test_tariff_remove(self):
		"""Check state changing with tariffRemove"""

		data = {
			'id':           unicode(uuid.uuid4()),
			'name':         str(uuid.uuid4()),
			'description':  str(uuid.uuid4()),
			'state':        tariffs.constants.STATE_ENABLED,
			'time_create':  int(time.time()),
			'time_destroy': 0,
		}

		with database.DBConnect() as db:
			db.insert('tariffs', data)

		wapi_tariffs.tariffRemove({'name':data['name']})

		data['state'] = tariffs.constants.STATE_DELETED
		data['time_destroy'] = int(time.time())

		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'id': data['id']})

		self.assertEquals(t1, data)

		with unithelper.mocker('bc.tariffs', 'remove', 'bc.wapi.wapi_tariffs'):
			self.assertEquals(wapi_tariffs.tariffRemove({'id':''}),
				unithelper.requestor({'message': 'Unable to remove tariff' }, 'servererror'))


	def test_tariff_modification(self):
		""" Check modification attributes with tariffModify"""

		data = {
			'id':           unicode(uuid.uuid4()),
			'name':         str(uuid.uuid4()),
			'description':  str(uuid.uuid4()),
			'state':        tariffs.constants.STATE_ENABLED,
			'time_create':  int(time.time()),
			'time_destroy': 0,
		}

		with database.DBConnect() as db:
			db.insert('tariffs', data)

		self.assertEqual(wapi_tariffs.tariffModify({'id':data['id']}),
				unithelper.requestor({}, 'ok'))

		data1 = {
			'id':           data['id'],
			'name':         str(uuid.uuid4()),
			'description':  str(uuid.uuid4()),
		}

		data.update(data1)


		self.assertEqual(wapi_tariffs.tariffModify(data1),
				unithelper.requestor({}, 'ok'))


		with unithelper.mocker('bc.tariffs', 'modify', 'bc.wapi.wapi_tariffs'):
			self.assertEquals(wapi_tariffs.tariffModify(data1),
				unithelper.requestor({'message': 'Unable to modify tariff' }, 'servererror'))

		self.assertEqual(
			wapi_tariffs.tariffModify({'id':'','state':tariffs.constants.STATE_DISABLED}),
			unithelper.requestor({'message': 'Wrong state: ' + str(tariffs.constants.STATE_DISABLED)}, 'error'))



		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'id': data['id']})

		self.assertEquals(t1, data)
