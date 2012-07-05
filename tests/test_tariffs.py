import unithelper
import uuid
import time

from bc import database
from bc import tariffs

class Test(unithelper.DBTestCase):

	def test_tariff_get(self):
		"""Check getting tariff from db"""

		data = {
			'id':           unicode(uuid.uuid4()),
			'name':         str(uuid.uuid4()),
			'description':  str(uuid.uuid4()),
			'state':        tariffs.constants.STATE_ENABLED,
			'time_create':  int(time.time()),
			'time_destroy': 0,
		}

		tar = tariffs.Tariff(data)

		with database.DBConnect() as db:
			db.insert('tariffs', data)

		self.assertEquals(tariffs.get(tar.id), tar)


	def test_tariff_get_all(self):
		"""Check getting tariffs from db"""

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

			data.append(tariffs.Tariff(d))

		self.assertEquals(set(list(tariffs.get_all())), set(data))


	def test_tariff_creation(self):
		"""Check the creating of the tariff"""

		tar = tariffs.Tariff(
			data={
				"name": str(uuid.uuid4()),
				"description": str(uuid.uuid4()),
			}
		)
		tariffs.add(tar)

		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'id':tar.id})
		self.assertEquals(tariffs.Tariff(t1), tar)


	def test_tariff_delete(self):
		"""Check state changing"""

		data = {
			'id':           unicode(uuid.uuid4()),
			'name':         str(uuid.uuid4()),
			'description':  str(uuid.uuid4()),
			'state':        tariffs.constants.STATE_ENABLED,
			'time_create':  int(time.time()),
			'time_destroy': 0,
		}

		tar = tariffs.Tariff(data)

		with database.DBConnect() as db:
			db.insert('tariffs', data)

		tariffs.remove('id', tar.id)
		tar.set({'state': tariffs.constants.STATE_DELETED,
			'time_destroy': int(time.time())})

		with self.assertRaises(ValueError):
			tariffs.remove('state', tar.id)

		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'id': tar.id})

		self.assertEquals(tariffs.Tariff(t1), tar)


	def test_tariff_modification(self):
		""" Check modification attributes"""

		data = {
			'id':           unicode(uuid.uuid4()),
			'name':         str(uuid.uuid4()),
			'description':  str(uuid.uuid4()),
			'state':        tariffs.constants.STATE_ENABLED,
			'time_create':  int(time.time()),
			'time_destroy': 0,
		}

		tar = tariffs.Tariff(data)

		with database.DBConnect() as db:
			db.insert('tariffs', data)

		data = {
			'name':         str(uuid.uuid4()),
			'description':  str(uuid.uuid4()),
			'state':        tariffs.constants.STATE_DISABLED,
				}
		tariffs.modify('id', tar.id, data)
		tar.set(data)

		with self.assertRaises(TypeError):
			tariffs.modify('id', tar.id, {'state':tariffs.constants.STATE_MAXVALUE+1})

		with self.assertRaises(ValueError):
			tariffs.modify('name', tar.id, {})

		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'id': tar.id})

		self.assertEquals(tariffs.Tariff(t1), tar)
