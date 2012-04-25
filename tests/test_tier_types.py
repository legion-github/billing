import unittest
import uuid

from billing import tier_types
from billing import exceptions

from c2.tests2 import testcase


class Test(testcase.MongoDBTestCase):

	def test_add_one(self):
		"""Check the addition new tier type"""

		tier_id = 1
		tier_name = "i"
		tier_replication = True
		tier_description = "Tier"

		t = tier_types.add_one(tier_id, tier_name, tier_replication, tier_description)
		tt = self.billing_database()["tier_types"].find_one({"_id": t["_id"]})
		self.assertNotEquals(tt["tier_id"], None)

		self.assertNotEquals(tt["_id"], "")

		self.assertEquals(tt["tier_id"], tier_id)
		self.assertEquals(tt["tier_name"], tier_name)
		self.assertEquals(tt["replication"], tier_replication)
		self.assertEquals(tt["description"], tier_description)

		self.assertRaises(exceptions.TierTypeExistsError,
			tier_types.add_one, tier_id, tier_name + "XXX", tier_replication, tier_description + "XXX")


	def test_rename_one(self):
		"""Check the removal tier type"""

		tier_id = 1
		tier_name = "i"
		tier_replication = True
		tier_description1 = str(uuid.uuid4())
		tier_description2 = str(uuid.uuid4())

		self.assertNotEquals(tier_description1, tier_description2)

		t = tier_types.add_one(tier_id, tier_name, tier_replication, tier_description1)
		tt1 = self.billing_database()["tier_types"].find_one({"_id": t["_id"]})
		self.assertEquals(tt1["description"], tier_description1)

		tier_types.rename_one(t["_id"], tier_description2)

		tt2 = self.billing_database()["tier_types"].find_one({"_id": t["_id"]})
		self.assertEquals(tt2["description"], tier_description2)

		self.assertRaises(exceptions.TierTypeError,
			lambda: tier_types.rename_one("unknown-id", ""))


	def test_find(self):
		"""Check the finding tier type"""

		tier_num = 3
		tier_list = [
			tier_types.add_one(i, n, True)
			for i,n in [ (1,"I"), (2,"II"), (3,"III") ]
		]

		self.assertEquals(tier_num, tier_types.find().count())

		t = tier_types.find(tier_list[0], "tier-unknown")
		self.assertEquals(1, t.count())
		self.assertEquals(t[0]["_id"], tier_list[0]["_id"])

		t = tier_types.find(tier_list[0], { "tier_id": True, "_id": False})
		self.assertEquals(1, t.count())
		tt = t[0]
		self.assertEquals(tt.get("_id"), None)
		self.assertNotEquals(tt.get("tier_id"), None)

