import uuid
import time
import random

from unithelper import DBTestCase
from unithelper import mocker
from unithelper import requestor
from unithelper import hashable_dict

from bc import database
from bc import customers

from bc_wapi import wapi_customers


class Test(DBTestCase):

	def test_customers_get(self):
		"""Check getting customer with customerGet"""

		data = {
			'id': str(uuid.uuid4()),
			'login': str(uuid.uuid4()),
			'name_short': str(uuid.uuid4()),
			'name_full': str(uuid.uuid4()),
			'comment': str(uuid.uuid4()),
			'contract_client': str(uuid.uuid4()),
			'contract_service': str(uuid.uuid4()),
			'tariff_id': str(uuid.uuid4()),
			'contact_person': str(uuid.uuid4()),
			'contact_email': str(uuid.uuid4()),
			'contact_phone': str(uuid.uuid4())[:10],
			'state': customers.constants.STATE_ENABLED,
			'time_create': int(time.time()),
			'time_destroy': 0,
			'wallet': 10,
			'wallet_mode': customers.constants.WALLET_MODE_LIMITED
		}

		with database.DBConnect() as db:
			db.insert('customers', data)

		self.assertEquals(wapi_customers.customerGet({'id': data['id']}),
				requestor({'customer': data}, 'ok'))

		self.assertEquals(wapi_customers.customerGet({'id':''}),
				requestor({'message': 'Customer not found' }, 'error'))

		with mocker([('bc.customers.get', mocker.exception),
					('bc_wapi.wapi_customers.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_customers.customerGet({'id':''}),
				requestor({'message': 'Unable to obtain customer' }, 'servererror'))


	def test_customers_get_list(self):
		"""Check getting customers with customerList"""

		cus = []
		for i in range(25):
			data = {
				'id': str(uuid.uuid4()),
				'login': str(uuid.uuid4()),
				'name_short': str(uuid.uuid4()),
				'name_full': str(uuid.uuid4()),
				'comment': str(uuid.uuid4()),
				'contract_client': str(uuid.uuid4()),
				'contract_service': str(uuid.uuid4()),
				'tariff_id': str(uuid.uuid4()),
				'contact_person': str(uuid.uuid4()),
				'contact_email': str(uuid.uuid4()),
				'contact_phone': str(uuid.uuid4())[:10],
				'state': random.choice([customers.constants.STATE_ENABLED,
										customers.constants.STATE_DELETED,
										customers.constants.STATE_DISABLED]),
				'time_create': int(time.time()),
				'time_destroy': 0,
				'wallet': 10,
				'wallet_mode': customers.constants.WALLET_MODE_LIMITED
				}

			with database.DBConnect() as db:
				db.insert('customers', data)

			cus.append(data)

		ans = wapi_customers.customerList('')
		self.assertEquals(ans[0], (01 << 2))
		self.assertEquals(ans[1]['status'], 'ok')

		self.assertEquals(set(map(lambda x: hashable_dict(x), ans[1]['customers'])),
				set(map(lambda x: hashable_dict(x),
					filter(lambda x: x['state'] == customers.constants.STATE_ENABLED, cus))))

		with mocker([('bc.customers.get_all', mocker.exception),
					('bc_wapi.wapi_customers.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_customers.customerList({'id':''}),
				requestor({'message': 'Unable to obtain customer list' }, 'servererror'))


	def test_customer_add(self):
		"""Check the creating tariff with customerAdd"""

		data={
			'id': str(uuid.uuid4()),
			'login': str(uuid.uuid4()),
			'name_short': str(uuid.uuid4()),
			'name_full': str(uuid.uuid4()),
			'comment': str(uuid.uuid4()),
			'contract_client': str(uuid.uuid4()),
			'contract_service': str(uuid.uuid4()),
			'tariff_id': str(uuid.uuid4()),
			'contact_person': str(uuid.uuid4()),
			'contact_email': str(uuid.uuid4()),
			'contact_phone': str(uuid.uuid4())[:10],
			'state': customers.constants.STATE_ENABLED,
			'time_create': int(time.time()),
			'time_destroy': 0,
			'wallet': 10,
			'wallet_mode': 'unlimit'
		}
		ans = wapi_customers.customerAdd(data)

		self.assertEquals(ans, requestor({'id':data['id']}, 'ok'))

		with database.DBConnect() as db:
			t1 = db.find('customers').one()
		self.assertEquals(data, t1)

		self.assertEquals(wapi_customers.customerAdd({'login':'',
			'wallet_mode':'',
			'name_short':''}), requestor({'message': 'Wrong wallet_mode: ' }, 'error'))

		with mocker([('bc.customers.add', mocker.exception),
					('bc_wapi.wapi_customers.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_customers.customerAdd({'id':''}),
				requestor({'message': 'Unable to add new customer' }, 'servererror'))


	def test_customer_remove(self):
		"""Check state changing with customerRemove"""

		data = {
			'id': str(uuid.uuid4()),
			'login': str(uuid.uuid4()),
			'name_short': str(uuid.uuid4()),
			'name_full': str(uuid.uuid4()),
			'comment': str(uuid.uuid4()),
			'contract_client': str(uuid.uuid4()),
			'contract_service': str(uuid.uuid4()),
			'tariff_id': str(uuid.uuid4()),
			'contact_person': str(uuid.uuid4()),
			'contact_email': str(uuid.uuid4()),
			'contact_phone': str(uuid.uuid4())[:10],
			'state': customers.constants.STATE_ENABLED,
			'time_create': int(time.time()),
			'time_destroy': 0,
			'wallet': 10,
			'wallet_mode': customers.constants.WALLET_MODE_LIMITED
		}

		with database.DBConnect() as db:
			db.insert('customers', data)

		self.assertEquals(wapi_customers.customerRemove({'id':data['id']}),
				requestor({}, 'ok'))

		data['state'] = customers.constants.STATE_DELETED
		data['time_destroy'] = int(time.time())

		with database.DBConnect() as db:
			t1 = db.find_one('customers', {'id': data['id']})

		self.assertEquals(t1, data)

		with mocker([('bc.customers.remove', mocker.exception),
					('bc_wapi.wapi_customers.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_customers.customerRemove({'id':''}),
				requestor({'message': 'Unable to remove customer' }, 'servererror'))


	def test_customers_modification(self):
		""" Check modification attributes with customerModify"""

		data = {
			'id': str(uuid.uuid4()),
			'login': str(uuid.uuid4()),
			'name_short': str(uuid.uuid4()),
			'name_full': str(uuid.uuid4()),
			'comment': str(uuid.uuid4()),
			'contract_client': str(uuid.uuid4()),
			'contract_service': str(uuid.uuid4()),
			'tariff_id': str(uuid.uuid4()),
			'contact_person': str(uuid.uuid4()),
			'contact_email': str(uuid.uuid4()),
			'contact_phone': str(uuid.uuid4())[:10],
			'state': customers.constants.STATE_ENABLED,
			'time_create': int(time.time()),
			'time_destroy': 0,
			'wallet': 10,
			'wallet_mode': customers.constants.WALLET_MODE_LIMITED
			}

		with database.DBConnect() as db:
			db.insert('customers', data)

		self.assertEqual(wapi_customers.customerModify({'id':data['id']}),
				requestor({}, 'ok'))

		data1 = {
			'login':        data['login'],
			'contact_email':         str(uuid.uuid4()),
			'tariff_id':  str(uuid.uuid4()),
		}

		data.update(data1)


		self.assertEqual(wapi_customers.customerModify(data1),
				requestor({}, 'ok'))


		with mocker([('bc.customers.modify', mocker.exception),
					('bc_wapi.wapi_customers.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_customers.customerModify(data1),
				requestor({'message': 'Unable to modify customer' }, 'servererror'))

		self.assertEqual(
			wapi_customers.customerModify({'login':'','state':customers.constants.STATE_DELETED}),
			requestor({'message': 'Wrong state: ' + str(customers.constants.STATE_DELETED)}, 'error'))

		self.assertEqual(
			wapi_customers.customerModify({'login':'','wallet_mode':''}),
			requestor({'message': 'Wrong wallet_mode: ' }, 'error'))


		with database.DBConnect() as db:
			t1 = db.find_one('customers', {'id': data['id']})

		self.assertEquals(t1, data)


	def test_customer_deposit(self):
		"""Check wallet changing with customerDeposit"""

		data = {
			'id': str(uuid.uuid4()),
			'login': str(uuid.uuid4()),
			'name_short': str(uuid.uuid4()),
			'name_full': str(uuid.uuid4()),
			'comment': str(uuid.uuid4()),
			'contract_client': str(uuid.uuid4()),
			'contract_service': str(uuid.uuid4()),
			'tariff_id': str(uuid.uuid4()),
			'contact_person': str(uuid.uuid4()),
			'contact_email': str(uuid.uuid4()),
			'contact_phone': str(uuid.uuid4())[:10],
			'state': customers.constants.STATE_ENABLED,
			'time_create': int(time.time()),
			'time_destroy': 0,
			'wallet': 10,
			'wallet_mode': customers.constants.WALLET_MODE_LIMITED
		}

		with database.DBConnect() as db:
			db.insert('customers', data)

		self.assertEquals(wapi_customers.customerDeposit({'id':data['id'],
			'value':0}),
				requestor({}, 'ok'))

		deposit = random.randint(1, 2**10)
		self.assertEquals(wapi_customers.customerDeposit({'id':data['id'],
			'value':deposit}),
				requestor({}, 'ok'))

		with database.DBConnect() as db:
			t1 = db.find_one('customers', {'id': data['id']})

		data['wallet'] += deposit

		self.assertEquals(t1, data)

		with mocker([('bc.customers.deposit', mocker.exception),
					('bc_wapi.wapi_customers.LOG.error', mocker.passs)]):
			self.assertEquals(wapi_customers.customerDeposit({'id':''}),
				requestor({'message': 'Unable to make a deposit' }, 'servererror'))
