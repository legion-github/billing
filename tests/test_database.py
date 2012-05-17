import unithelper
import uuid
import time

import unittest2 as unittest
from bc import database


class Test(unithelper.DBTestCase):
	def setUp(self):
		with database.DBConnect() as db:
			test_base_dropper = """
			DROP TABLE IF EXISTS `new_table`;
			"""
			test_base_creator="""
			CREATE TABLE `new_table` (
			`uuid` varchar(36) NOT NULL,
			`big` bigint(20) NOT NULL,
			`time` int(11) NOT NULL,
			 PRIMARY KEY (`uuid`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
			"""
			db.connect().cursor().execute(test_base_dropper)
			db.connect().cursor().execute(test_base_creator)


	@unittest.skipUnless(unithelper.haveDatabase(), True)
	def test_insert(self):
		"""insert test"""
		with database.DBConnect() as db:
			dictionary = {
					'uuid': str(uuid.uuid4()),
					'big': 2**32,
					'time': int(time.time())
					}
			db.insert('new_table', dictionary)
			c = db.query("SELECT * FROM `new_table` WHERE `uuid`='{0}';".format(dictionary['uuid']))
			self.assertEqual(dictionary, c.next())


	@unittest.skipUnless(unithelper.haveDatabase(), True)
	def test_update(self):
		"""update test"""
		with database.DBConnect() as db:
			dictionary = {
					'uuid': str(uuid.uuid4()),
					'big': 2**32,
					'time': int(time.time())
					}

			db.insert('new_table', dictionary)

			dictionary['big'] = 2**30
			dictionary['time'] = int(time.time())
			dset = dictionary.copy()
			dsearch = {'uuid':dset['uuid']}
			del(dset['uuid'])
			db.update('new_table', dsearch, dset)

			c = db.query("SELECT * FROM `new_table` WHERE `uuid`='{0}';".format(dictionary['uuid']))
			self.assertEqual(dictionary, c.next())
