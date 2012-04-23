import unittest

from billing import tariffs_map

from c2.tests2 import testcase, utils


class TariffsMapTest(testcase.MongoDBTestCase):

	def test_add(self):
		""" tm_add() """

		tariff_id, customer_id, user_id = 't1', 'c1', 'u1'

		rec_id = tariffs_map.tm_add(tariff_id, customer_id, user_id)
		rec = self.billing_database()['tariffmap'].find_one({'_id': rec_id})

		self.assertNotEquals(rec['_id'], None)
		self.assertNotEquals(rec["_id"], "")

		self.assertEquals(rec['tariff_id'],   tariff_id)
		self.assertEquals(rec['customer_id'], customer_id)
		self.assertEquals(rec['user_id'],     user_id)


	def test_remove(self):
		""" tm_remove() """

		rec_id = tariffs_map.tm_add('t0', 'c0', 'u0')
		rec_id = tariffs_map.tm_add('t2', 'c2', 'u2')

		self.assertFalse(tariffs_map.tm_remove('FOOBAR', rec_id))
		self.assertTrue(tariffs_map.tm_remove('record', rec_id))

		tariff_id, customer_id, user_id = 't1', 'c1', 'u1'

		for i,n in [(tariff_id, 'tariff'), (customer_id, 'customer'), (user_id, 'user')]:
			tariffs_map.tm_add(tariff_id, customer_id, user_id)
			self.assertTrue(tariffs_map.tm_remove(n, i))

		n = self.billing_database()['tariffmap'].find().count()
		self.assertEquals(n, 1)


	def test_change_tariff(self):
		""" tm_change_tariff() """

		tariffs_map.tm_add('t0', 'c0', 'u0')
		tariffs_map.tm_add('t0', 'c0', 'u1')
		tariffs_map.tm_add('t1', 'c1', 'u3')

		tariffs_map.tm_change_tariff('c0', 't2')

		t = []
		for n in self.billing_database()['tariffmap'].find({'customer_id': 'c0'}, fields={'tariff_id':True}):
			if n['tariff_id'] not in t:
				t.append(n['tariff_id'])
		self.assertEquals(1, len(t))
		self.assertEquals('t2', t[0])

		n = self.billing_database()['tariffmap'].find_one({'customer_id': 'c1'}, fields={'tariff_id':True})
		self.assertEquals('t1', n['tariff_id'])


	def test_find(self):
		""" tm_find() """

		r1 = tariffs_map.tm_add('t0', 'c0', 'u1')
		r2 = tariffs_map.tm_add('t0', 'c0', 'u2')
		r3 = tariffs_map.tm_add('t1', 'c1', 'u3')

		r = tariffs_map.tm_find('user', 'u2', fields = {'_id':True})
		self.assertEquals(1, len(r))
		self.assertEquals(r2, r[0]['_id'])

		l = []
		for r in tariffs_map.tm_find('customer', 'c0', fields = {'_id':True}):
			l.append(r['_id'])

		self.assertEquals(2, len(l))
		self.assertEquals(set([r1, r2]), set(l))


	def test_find_one(self):
		""" tm_find_one() """

		r1 = tariffs_map.tm_add('t0', 'c0', 'u1')
		r2 = tariffs_map.tm_add('t0', 'c0', 'u2')
		r3 = tariffs_map.tm_add('t1', 'c1', 'u3')

		r = tariffs_map.tm_find_one('user', 'u2', fields = {'_id':True})
		self.assertEquals(r2, r['_id'])


if __name__ == '__main__':
	utils.run_tests(TariffsMapTest)
