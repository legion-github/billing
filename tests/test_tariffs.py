import unittest
import uuid

from billing import constants
from billing import tariffs
from billing import exceptions

from c2.tests2 import testcase


class Test(testcase.MongoDBTestCase):

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

		t1 = self.billing_database()["tariffs"].find_one({"_id": tariff_id})
		self.assertEquals(t1["name"], tariff_name1)
		self.assertEquals(t1["description"], tariff_description1)

		tariffs.rename_tariff(tariff_id, tariff_name2, tariff_description2)

		t2 = self.billing_database()["tariffs"].find_one({ "_id": tariff_id })
		self.assertEquals(t2["name"], tariff_name2)
		self.assertEquals(t2["description"], tariff_description2)

		self.assertRaises(Exception,
			lambda: tariffs.rename_tariff("unknown-id", "", ""))
