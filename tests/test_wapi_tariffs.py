import uuid
import time

from unithelper import DBTestCase
from unithelper import mocker
from unithelper import requestor
from unithelper import hashable_dict

from bc import database
from bc import tariffs

from bc_wapi import wapi_tariffs


class Test(DBTestCase):

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
				requestor({'tariff': data}, 'ok'))

		self.assertEquals(wapi_tariffs.tariffGet({'id':''}),
				requestor({'message': 'Tariff not found' }, 'error'))

		with mocker([('bc.tariffs.get', mocker.exception),
					('bc_wapi.wapi_tariffs.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_tariffs.tariffGet({'id':''}),
				requestor({'message': 'Unable to obtain tariff' }, 'servererror'))


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

		self.assertEquals(set(map(lambda x: hashable_dict(x), ans[1]['tariffs'])),
				set(map(lambda x: hashable_dict(x), data)))

		with mocker([('bc.tariffs.get_all', mocker.exception),
					('bc_wapi.wapi_tariffs.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_tariffs.tariffList({'id':''}),
				requestor({'message': 'Unable to obtain tariff list' }, 'servererror'))


	def test_tariff_add(self):
		"""Check the creating tariff with tariffAdd"""

		data={
			'id':   str(uuid.uuid4()),
			'name': str(uuid.uuid4()),
			'description': str(uuid.uuid4()),
		}
		ans = wapi_tariffs.tariffAdd(data.copy())

		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'name':data['name']})
		self.assertEquals(data['name'], t1['name'])
		self.assertEquals(data['description'], t1['description'])

		self.assertEquals(ans, requestor({'id':t1['id']}, 'ok'))

		with mocker([('bc.tariffs.add', mocker.exception),
					('bc_wapi.wapi_tariffs.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_tariffs.tariffAdd({'id':''}),
				requestor({'message': 'Unable to add new tariff' }, 'servererror'))


	def test_tariff_add_internal(self):
		"""Check the creating tariff with tariffAddInternal"""

		data={
			'id': str(uuid.uuid4()),
			'name': str(uuid.uuid4()),
			'description': str(uuid.uuid4()),
		}
		ans = wapi_tariffs.tariffAdd(data)

		self.assertEquals(ans, requestor({'id':data['id']}, 'ok'))

		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'id': data['id']})
		self.assertEquals(data['name'], t1['name'])
		self.assertEquals(data['description'], t1['description'])

		with mocker([('bc.tariffs.add', mocker.exception),
					('bc_wapi.wapi_tariffs.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_tariffs.tariffAdd({'id':''}),
				requestor({'message': 'Unable to add new tariff' }, 'servererror'))


	def test_tariff_remove(self):
		"""Check state changing with tariffRemove"""

		data = {
			'id':           unicode(uuid.uuid4()),
			'name':         str(uuid.uuid4()),
			'description':  str(uuid.uuid4()),
			'state':        tariffs.constants.STATE_ENABLED,
			'time_create':  int(time.time()),
			'time_destroy': 0,
			'sync':         0,
		}

		with database.DBConnect() as db:
			db.insert('tariffs', data)

		wapi_tariffs.tariffRemove({'id':data['id']})

		data['state'] = tariffs.constants.STATE_DELETED
		data['time_destroy'] = int(time.time())

		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'id': data['id']})

		self.assertEquals(t1, data)

		with mocker([('bc.tariffs.remove', mocker.exception),
					('bc_wapi.wapi_tariffs.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_tariffs.tariffRemove({'id':''}),
				requestor({'message': 'Unable to remove tariff' }, 'servererror'))


	def test_tariff_modification(self):
		""" Check modification attributes with tariffModify"""

		data = {
			'id':           unicode(uuid.uuid4()),
			'name':         str(uuid.uuid4()),
			'description':  str(uuid.uuid4()),
			'state':        tariffs.constants.STATE_ENABLED,
			'time_create':  int(time.time()),
			'time_destroy': 0,
			'sync':         0,
		}

		with database.DBConnect() as db:
			db.insert('tariffs', data)

		self.assertEqual(wapi_tariffs.tariffModify({'id':data['id']}),
				requestor({}, 'ok'))

		data1 = {
			'id':           data['id'],
			'name':         str(uuid.uuid4()),
			'description':  str(uuid.uuid4()),
		}

		data.update(data1)


		self.assertEqual(wapi_tariffs.tariffModify(data1),
				requestor({}, 'ok'))


		with mocker([('bc.tariffs.modify', mocker.exception),
					('bc_wapi.wapi_tariffs.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_tariffs.tariffModify(data1),
				requestor({'message': 'Unable to modify tariff' }, 'servererror'))

		self.assertEqual(
			wapi_tariffs.tariffModify({'id':'','state':tariffs.constants.STATE_DISABLED}),
			requestor({'message': 'Wrong state: ' + str(tariffs.constants.STATE_DISABLED)}, 'error'))

		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'id': data['id']})

		self.assertEquals(t1, data)
