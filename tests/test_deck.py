import time
import uuid
import pymongo

from pymongo.errors import DuplicateKeyError
from c2             import mongodb
from c2.tests2      import testcase, utils

from bc.private     import deck

deckname = 'test-deck'
bad_deckname = 'unknown-test-deck'

class DeckTest(testcase.UserTestCase):
	def setUp(self):
		testcase.UserTestCase.setUp(self)
		self.billing_database()['queue-' + deckname].ensure_index([(deck.UID, pymongo.ASCENDING)], unique = True)


	def test_create(self):
		"""create()"""

		deck.create(deckname, None, self.user["uuid"], {'data': 1})
		deck.create(deckname, None, self.user["uuid"], {'data': 2})
		deck.create(deckname, None, self.user["uuid"], {'data': 3})
		self.assertEquals(3, deck.size(deckname))

		deck.create(deckname, "ID", self.user["uuid"], {'data': 4})
		self.assertEquals(4, deck.size(deckname))


	def test_recreate(self):
		"""recreate()"""

		deck.create(deckname, "ID", self.user["uuid"], {'data': 4})
		deck.recreate_forever(deckname, "ID", {'data':5})
		deck.recreate_forever(deckname, "ID", {'data':5})

		alive = mongodb.billing_collection('queue-'+deckname).find({'time-destroy': 0}).count()
		dead = mongodb.billing_collection('queue-'+deckname).find({'time-destroy': {'$ne':0}}).count()
		self.assertEquals(1, alive)
		self.assertEquals(2, dead)


	def test_get(self):
		"""get()"""

		deck.create(deckname, None, self.user["uuid"], {'data': 1})
		deck.create(deckname, None, self.user["uuid"], {'data': 2})
		deck.create(deckname, None, self.user["uuid"], {'data': 3})
		time.sleep(2)

		for i in xrange(1, 4):
			t = deck.get(deckname, to_time = int(time.time()))
			self.assertNotEquals(None, t)
			self.assertEquals({'data': i}, t[deck.DATA])

		t = deck.get(deckname)
		self.assertEquals(None, t)

		t = deck.get(bad_deckname)
		self.assertEquals(None, t)


	def test_get_remove(self):
		"""get_remove()"""

		deck.create(deckname, None, self.user["uuid"], {'data': 1})
		time.sleep(2)

		t = deck.get(deckname, to_time = int(time.time()), remove = True)
		self.assertEquals({'data': 1}, t[deck.DATA])
		t = deck.get(deckname, to_time = int(time.time()))
		self.assertEquals(None, t)


	def test_save(self):
		"""save()"""

		deck.create(deckname, None, self.user["uuid"], {'data': 1})
		time.sleep(2)

		t = deck.get(deckname, to_time = int(time.time()))
		d = t[deck.DATA]
		d['data'] = 2

		deck.save(t)

		t = deck.get(deckname, to_time = int(time.time()))
		self.assertEquals({'data': 2}, t[deck.DATA])


	def test_remove(self):
		"""remove()"""

		deck.create(deckname, None, self.user["uuid"], {'data': 1})
		time.sleep(2)

		t = deck.get(deckname, to_time = int(time.time()))
		self.assertEquals({'data': 1}, t[deck.DATA])

		deck.remove(t)
		t = deck.get(deckname, to_time = int(time.time()))
		self.assertEquals(None, t)


	def test_delete(self):
		"""delete()"""
		
		deck.create(deckname, None, self.user["uuid"], {'data': 1})
		time.sleep(2)

		t = deck.get(deckname, to_time = int(time.time()))
		deck.delete(deckname, t["uuid"], remove = False)
		self.assertNotEquals(mongodb.billing_collection('queue-'+deckname).find()[0]['time-destroy'], 0)
		deck.delete(deckname, t["uuid"], remove = True)
		self.assertEquals(list(mongodb.billing_collection('queue-'+deckname).find()), [])


	def test_race1(self):
		"""recreate in recreate"""

		deck.create(deckname, "ID", self.user["uuid"], {'data': 4})
		self.__recreate(deckname, "ID", {'data':5},race=deck.recreate, args={'name':deckname, 'uid':"ID", 'udata':{'data':6}})
		alive = mongodb.billing_collection('queue-'+deckname).find({'time-destroy': 0}).count()
		dead = mongodb.billing_collection('queue-'+deckname).find({'time-destroy': {'$ne':0}}).count()
		all = mongodb.billing_collection('queue-'+deckname).find().count()

		self.assertEquals(1, alive)
		self.assertEquals(1, dead)
		self.assertEquals(2, all)


	def test_race2(self):
		"""tariff_change recreate in recreate"""

		deck.create(deckname, "ID", self.user["uuid"], {'data': 4})
		new_tariff=uuid.uuid4()

		self.__recreate(deckname, "ID", {'data':5},race=deck.recreate, args={'name':deckname, 'uid':"ID", 'udata':{'data':4}, 'values':{'tariff':new_tariff}})
		alive = mongodb.billing_collection('queue-'+deckname).find({'time-destroy': 0, 'info.data':5}).count()
		dead = mongodb.billing_collection('queue-'+deckname).find({'time-destroy': {'$ne':0}, 'info.data':4}).count()
		new = mongodb.billing_collection('queue-'+deckname).find({'tariff': new_tariff}).count()
		all = mongodb.billing_collection('queue-'+deckname).find().count()

		self.assertEquals(1, alive)	# alive resized, but with old tariff (job for gc)
		self.assertEquals(0, new)	# tariff change fail
		self.assertEquals(1, dead)	# dead have old size
		self.assertEquals(2, all)	# no trash


	def test_race3(self):
		"""delete in recreate"""

		deck.create(deckname, "ID", self.user["uuid"], {'data': 4})

		self.__recreate(deckname, "ID", {'data':5},race=deck.delete, args={'name':deckname, 'uid':"ID", 'remove': False})

		alive = mongodb.billing_collection('queue-'+deckname).find({'time-destroy': 0, 'info.data':5}).count()
		dead = mongodb.billing_collection('queue-'+deckname).find({'time-destroy': {'$ne':0}, 'info.data':4}).count()
		all = mongodb.billing_collection('queue-'+deckname).find().count()

		self.assertEquals(0, alive)	# alive resized and deleted
		self.assertEquals(1, dead)	# dead have old size
		self.assertEquals(1, all)	# no trash


	def test_race4(self):
		"""delete before recreate"""

		deck.create(deckname, "ID", self.user["uuid"], {'data': 4})
		deck.delete(deckname, "ID")
		deck.recreate(deckname, "ID", {'data':5})

		alive = mongodb.billing_collection('queue-'+deckname).find({'time-destroy': 0, 'info.data':5}).count()
		dead = mongodb.billing_collection('queue-'+deckname).find({'time-destroy': {'$ne':0}, 'info.data':4}).count()
		all = mongodb.billing_collection('queue-'+deckname).find().count()

		self.assertEquals(0, alive)	# alive resized and deleted
		self.assertEquals(1, dead)	# dead have old size
		self.assertEquals(1, all)	# no trash


	def __recreate(self, name, uid, udata, values = None, race=lambda:None, args={}):
		"""whis is copy of deck.recreate whith added points for injecting code for race"""
		# nekolyanich FIXME
		
		STATE_PROCESSING = 'processing'
		UID          = 'uuid'
		NAME         = 'queue'
		CUSTOMER     = 'customer'
		USER         = 'user'
		TARIFF       = 'tariff'
		STATE        = 'state'
		TIME_CREATE  = 'time-create'
		TIME_CHECK   = 'time-check'
		TIME_DESTROY = 'time-destroy'
		DATA         = 'info'
		now = int(time.time())
		old = mongodb.billing_collection('queue-' + name).find_and_modify(
			{
				UID: uid,
				TIME_DESTROY: 0
			},
			{
				'$set': {
					UID: uid + '--' + str(uuid.uuid4()),
					TIME_DESTROY: now
				}
			}
		)
		race(**args)
		if old:
			if values:
				old.update(values)

			try:
				mongodb.billing_collection('queue-' + name).update(
					{
						UID: uid,
						TIME_DESTROY: 0
					},
					{
						'$set': {
							NAME:        old[NAME],
							TARIFF:      old[TARIFF],
							CUSTOMER:    old[CUSTOMER],
							USER:        old[USER],
							STATE:       STATE_PROCESSING,
							TIME_CREATE: now,
							TIME_CHECK:  now,
							DATA:        dict(udata),
						}
					},
					upsert = True,
					safe = True
				)
			except DuplicateKeyError:
				o = mongodb.billing_collection('queue-' + name).find_one({UID: uid})
				if set(['_id', UID, TIME_DESTROY]) == set(o.keys()):
					mongodb.billing_collection('queue-' + name).remove(o)
			return True
		else:
			return False


if __name__ == '__main__':
	utils.run_tests(DeckTest)
