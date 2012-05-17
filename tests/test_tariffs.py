import unithelper
import uuid

from bc import database

from bc.private import tariff

class Test(unithelper.DBTestCase):

	def test_tariff_creation(self):
		"""Check the creating of the tariff"""

		tariff_name1 = str(uuid.uuid4())

		tariff_description1 = str(uuid.uuid4())

		tar = tariff.Tariff(
			data={
				"name": tariff_name1,
				"description": tariff_description1,
				"currency": 'USD'
			}
		)
		tar.create()
		with database.DBConnect() as db:
			t1 = db.query("SELECT * FROM `tariffs` WHERE `tariff_id`='{0}';".format(tar.values['tariff_id'])).one()
		self.assertEquals(t1["name"], tariff_name1)
		self.assertEquals(t1["description"], tariff_description1)


	def test_tariff_delete(self):
		"""Check state changing"""

		tariff_name1 = str(uuid.uuid4())

		tariff_description1 = str(uuid.uuid4())

		tar = tariff.Tariff(
			data={
				"name": tariff_name1,
				"description": tariff_description1,
				"currency": 'USD'
			}
		)
		tar.create()
		tar.set_state("DISABLE")

		with database.DBConnect() as db:
			t1 = db.query("SELECT * FROM `tariffs` WHERE `tariff_id`='{0}';".format(tar.values['tariff_id'])).one()
		self.assertEquals(t1["state"], "DISABLE")
