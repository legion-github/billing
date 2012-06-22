import unithelper
import uuid
import time

from bc import database
from bc import tariffs

class Test(unithelper.DBTestCase):

	def test_tariff_creation(self):
		"""Check the creating of the tariff"""

		tariff_name1 = str(uuid.uuid4())

		tariff_description1 = str(uuid.uuid4())

		tar = tariffs.Tariff(
			data={
				"name": tariff_name1,
				"description": tariff_description1,
				"currency": 'USD'
			}
		)
		tariffs.add(tar)
		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'id':tar.id})
		self.assertEquals(tariffs.Tariff(t1), tar)


	def test_tariff_delete(self):
		"""Check state changing"""

		tariff_name1 = str(uuid.uuid4())

		tariff_description1 = str(uuid.uuid4())

		tar = tariffs.Tariff(
			data={
				"name": tariff_name1,
				"description": tariff_description1,
				"currency": 'USD'
			}
		)
		tariffs.add(tar)
		tariffs.remove('id', tar.id)
		tar.set({'state': tariffs.constants.STATE_DELETED,
			'time_destroy': int(time.time())})

		with database.DBConnect() as db:
			t1 = db.find_one('tariffs', {'id': tar.id})

		self.assertEquals(tariffs.Tariff(t1), tar)
