import uuid

from c2.aws import exceptions

from bc.private.rate import Rate
from billing      import customers

from c2.tests2 import testcase

class Test(testcase.TariffTestCase):
	"""c2.wallets library test"""

	def test_create(self):
		"""Check the wallet creation"""

		q = customers.add({"name": str(uuid.uuid4()), "tariff": self.tariff_id})
		c = self.billing_database()["customers"].find_one({"_id": q["_id"]})

		self.assertNotEquals(None, c)
		self.assertEquals(0, c["wallet"])

	def test_deposit_1(self):
		"""Check the deposit to wallet (simple operations)"""

		q = customers.add({"name": str(uuid.uuid4()), "tariff": self.tariff_id})

		for ammount in [None, -1, "10"]:
			self.assertRaises(exceptions.InvalidParameterValue, lambda: customers.deposit(q["_id"], ammount))

		ammount = 100
		customers.deposit(q["_id"], ammount)
		self.assertEquals(ammount, customers.get(q["_id"])["wallet"])

		customers.deposit(q["_id"], ammount)
		self.assertEquals(ammount * 2, customers.get(q["_id"])["wallet"])

	def test_deposit_2(self):
		"""Check the deposit to wallet (overflow)"""

		ammount = ((1L << 32) - 1)
		num = 3

		q = customers.add({"name": str(uuid.uuid4()), "tariff": self.tariff_id})

		for i in xrange(0, num):
			customers.deposit(q["_id"], ammount)

		self.assertEquals(ammount * num, customers.get(q["_id"])["wallet"])

	def test_withdraw(self):
		"""Check the withdraw"""

		q = customers.add({"name": str(uuid.uuid4()), "tariff": self.tariff_id})

		value = 100
		customers.deposit(q["_id"], value)
		self.assertEquals(value, customers.get(q["_id"])["wallet"])

		customers.withdraw(q["_id"], Rate(value * 10 ** 33))
		self.assertEquals(0, customers.get(q["_id"])["wallet"])
