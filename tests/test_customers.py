import unithelper
import uuid
import time
import random

from bc import customers
from bc import database

class Test(unithelper.DBTestCase):
	def test_new_metric(self):
		"""Check tariff's rate object"""

		fields = [
			'id',
			'login',
			'name_short',
			'name_full',
			'comment',
			'contract_client',
			'contract_service',
			'tariff_id',
			'contact_person',
			'contact_email',
			'contact_phone',
			'state',
			'time_create',
			'time_destroy',
			'wallet',
			'wallet_mode'
		]

		c = customers.Customer()
		self.assertEqual(set(c.values.keys()), set(fields))


	def test_customers_get(self):
		"""Check getting customer from db"""

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

		cus = customers.Customer(data)

		with database.DBConnect() as db:
			db.insert('customers', data)

		with self.assertRaises(ValueError):
			customers.get('', random.choice(list(set(data.keys())-set(['login', 'id']))))

		self.assertEquals(customers.get(cus.id, 'id'), cus)

		self.assertEquals(customers.get(cus.login, 'login'), cus)


	def test_customers_get_all(self):
		"""Check getting customers from db"""

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

			cus.append( customers.Customer(data) )

			with database.DBConnect() as db:
				db.insert('customers', data)

		self.assertEquals(set(list(customers.get_all())),
			set(filter(lambda x: x.state==customers.constants.STATE_ENABLED, cus)))


	def test_customer_creation(self):
		"""Check the creating of customer"""

		cus = customers.Customer({
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
			'state': customers.constants.STATE_MAXVALUE,
			'time_create': int(time.time()),
			'time_destroy': 0,
			'wallet': 10,
			'wallet_mode': customers.constants.WALLET_MODE_LIMITED
		}
		)

		with self.assertRaises(TypeError):
			customers.add(cus)

		cus.set({'state': customers.constants.STATE_ENABLED,
			'wallet_mode': customers.constants.WALLET_MODE_MAXVALUE})
		with self.assertRaises(TypeError):
			customers.add(cus)

		cus.set({'wallet_mode': customers.constants.WALLET_MODE_LIMITED})
		customers.add(cus)

		with database.DBConnect() as db:
			c1 = db.find_one('customers', {'id':cus.id})

		self.assertEquals(customers.Customer(c1), cus)


	def test_customer_delete(self):
		"""Check state changing"""

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
		cus = customers.Customer(data)

		with database.DBConnect() as db:
			db.insert('customers', data)

		cus.set({'state': customers.constants.STATE_DELETED,
			'time_destroy': int(time.time())})

		with self.assertRaises(ValueError):
			customers.remove(random.choice(list(set(data.keys())-set(['login', 'id']))), cus.id)

		customers.remove('id', cus.id)

		with database.DBConnect() as db:
			c1 = db.find_one('customers', {'id': cus.id})

		self.assertEquals(customers.Customer(c1), cus)


	def test_customer_modification(self):
		""" Check modification attributes"""

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
		cus = customers.Customer(data)

		with database.DBConnect() as db:
			db.insert('customers', data)

		data = {'comment':  str(uuid.uuid4())}
		customers.modify('id', cus.id, data)
		cus.set(data)

		with self.assertRaises(ValueError):
			customers.modify(random.choice(list(set(data.keys())-set(['login', 'id']))), cus.id, {})
		with self.assertRaises(TypeError):
			customers.modify('id', cus.id, {'state':customers.constants.STATE_MAXVALUE})

		with self.assertRaises(TypeError):
			customers.modify('id', cus.id, {'wallet_mode':customers.constants.WALLET_MODE_MAXVALUE})

		with database.DBConnect() as db:
			c1 = db.find_one('customers', {'id': cus.id})

		self.assertEquals(customers.Customer(c1), cus)


	def test_customer_deposit(self):
		"""Check wallet incrimention"""

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
		cus = customers.Customer(data)

		with database.DBConnect() as db:
			db.insert('customers', data)

		value = 2**random.randint(3, 10)
		customers.deposit(cus.id, value)

		cus.set({'wallet': cus.wallet+value})

		with database.DBConnect() as db:
			c1 = db.find_one('customers', {'id': cus.id})

		self.assertEquals(customers.Customer(c1), cus)
