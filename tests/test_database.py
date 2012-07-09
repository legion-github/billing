import unithelper
import uuid
import time
import random

import unittest2 as unittest
from bc import database


class Test(unithelper.DBTestCase):
	def setUp(self):
		with database.DBConnect() as db:
			test_base_dropper = """
			DROP TABLE IF EXISTS new_table;
			"""
			test_base_creator="""
			CREATE TABLE new_table (
			uuid varchar(36) NOT NULL PRIMARY KEY,
			big bigint NOT NULL,
			time int NOT NULL
			);
			"""
			db.connect().cursor().execute(test_base_dropper)
			db.connect().cursor().execute(test_base_creator)
			db.connect().commit()


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
			c = db.query("SELECT * FROM new_table WHERE uuid='{0}';".format(dictionary['uuid']))
			self.assertEqual(dictionary, c.one())


	def test_insert_return(self):
		"""insert with return test"""
		with database.DBConnect() as db:
			o = {
				'uuid': str(uuid.uuid4()),
				'big': 2**32,
				'time': int(time.time())
			}

			c = db.insert('new_table', o, returning={})
			self.assertEqual(o, c.one())


	@unittest.skipUnless(unithelper.haveDatabase(), True)
	def test_insert_autocommit_false(self):
		"""transaction insert test"""
		with database.DBConnect(commit=False) as db:
			data = []
			for i in range(random.randint(5,10)):
				dictionary = {
						'uuid': str(uuid.uuid4()),
						'big': 2**32,
						'time': int(time.time())
						}
				db.insert('new_table', dictionary)
				data.append(dictionary)


			with database.DBConnect() as db1:
			#Must return empty set, because not commited yet
				self.assertEqual(
						set(),
						set(list(db1.query("SELECT * FROM new_table;").all()))
						)

			get_id = lambda x:x['uuid']
			#Must return all inserted data, because in transaction
			self.assertEqual(
					set(map(get_id, data)),
					set(map(get_id, db.query("SELECT * FROM new_table;").all()))
					)

			db.commit()
		with database.DBConnect() as db2:
		#Must return all inserted data, because transaction was commited
			self.assertEqual(
					set(map(get_id, data)),
					set(map(get_id, db2.query("SELECT * FROM new_table;").all()))
					)



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

			c = db.query("SELECT * FROM new_table WHERE uuid='{0}';".format(dictionary['uuid']))
			self.assertEqual(dictionary, c.one())


	@unittest.skipUnless(unithelper.haveDatabase(), True)
	def test_update_return(self):
		"""update with return test"""
		with database.DBConnect() as db:
			uid = str(uuid.uuid4())
			ts  = int(time.time())

			db.insert('new_table', { 'uuid':uid, 'big':2**32, 'time':ts })
			c = db.update('new_table', { 'uuid': uid }, { 'big': 2**30 }, returning={})

			self.assertEqual(c.all(), [{ 'uuid':uid, 'big':2**30, 'time':ts }])

