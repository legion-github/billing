import unittest2 as unittest
import unithelper

import pymongo

from bc import config
from bc import mongodb

def haveDatabase():
	try:
		c = pymongo.Connection('127.0.0.1')
		c.disconnect()
	except pymongo.errors.ConnectionFailure:
		return False
	return True


confstr = """
{
	"database": {
		"name":"testing",
		"server":"127.0.0.1",
		"shards":["127.0.0.10","127.0.0.11","127.0.0.12","127.0.0.13","127.0.0.14"]
	}
}
"""

conf = config.read(inline = confstr, force=True)

class Test(unithelper.DBTestCase):
	@unittest.skipUnless(haveDatabase(), True)
	def test_connect_mongo1(self):
		"""Check mongo connecting to global server"""

		c = mongodb.collection("testing")
		self.assertEqual(c.connection.host, "127.0.0.1")
		#c.insert({'foo':1})


	@unittest.skipUnless(haveDatabase(), True)
	def test_connect_mongo2(self):
		"""Check mongo connecting to shards"""

		c = mongodb.collection("testing", "qwerty")
		self.assertEqual(c.connection.host, "127.0.0.11")

		c = mongodb.collection("testing", "123456")
		self.assertEqual(c.connection.host, "127.0.0.13")
