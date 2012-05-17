import unithelper
import uuid

from bc import database

from billing import constants
from billing import tariffs

class Test(unithelper.DBTestCase):

	def test_rename_tariff(self):
		"""Check the renaming of the tariff"""

		tariff_name1 = str(uuid.uuid4())
		tariff_name2 = str(uuid.uuid4())

		tariff_description1 = str(uuid.uuid4())
		tariff_description2 = str(uuid.uuid4())

		tariff_id = tariffs.create(
			{
				"name": tariff_name1,
				"description": tariff_description1,
				"currency": constants.CURRENCY_LIST[0]
			},
			strict_check=False
		)

		with database.DBConnect() as db:
			t1 = db.query("SELECT * FROM `tariffs` WHERE `tariff_id`='{0}'".format(tariff_id)).next()
		self.assertEquals(t1["name"], tariff_name1)
		self.assertEquals(t1["description"], tariff_description1)

		tariffs.rename_tariff(tariff_id, tariff_name2, tariff_description2)

		with database.DBConnect() as db:
			t2 = db.query("SELECT * FROM `tariffs` WHERE `tariff_id`='{0}'".format(tariff_id)).next()
		self.assertEquals(t2["name"], tariff_name2)
		self.assertEquals(t2["description"], tariff_description2)

		self.assertRaises(Exception,
			lambda: tariffs.rename_tariff("unknown-id", "", ""))
