import uuid
import time
import unithelper

from bc import database
from bc import tasks

class Test(unithelper.DBTestCase):
	def test_new_task(self):
		"""Check task creation"""

		now = int(time.time())
		values = {
			'task_id':        'qqq',
			'base_id':        '123',
			'record_id':      '0',
			'queue_id':       '',
			'group_id':       0,
			'customer':       '',
			'rate_id':        '',
			'metric_id':      '',
			'state':          tasks.constants.STATE_ENABLED,
			'rate':           0L,
			'value':          0L,
			'time_create':    now,
			'time_destroy':   0,
			'target_user':    '',
			'target_uuid':    '',
			'target_descr':   '',
		}

		t = tasks.Task()
		t.set({'base_id':'123', 'task_id':'qqq'})

		self.assertEqual(set(t.values.keys()), set(values.keys()))
		self.assertEqual(set(t.values.values()), set(values.values()))


	def test_change_task(self):
		"""Check task modification"""

		t = tasks.Task()

		with self.assertRaises(TypeError):
			t.base_id = 123

		with self.assertRaises(KeyError):
			t.zzz = 1

		with self.assertRaises(ValueError):
			del t.zzz

		with self.assertRaises(KeyError):
			t.values = {}

		with self.assertNotRaises(TypeError):
			t.base_id = '123'

		with self.assertNotRaises(TypeError):
			t.values['base_id'] = '123'


	def test_task_creation(self):
		"""Check add new task to database"""

		o = tasks.Task({
			"name":     str(uuid.uuid4()),
			"customer": str(uuid.uuid4()),
			"rate_id":  str(uuid.uuid4()),
			"queue_id": str(uuid.uuid4()),
		})

		tasks.add(o)

		with database.DBConnect(primarykey=o.base_id) as db:
			n = db.find_one('tasks', {'base_id':o.base_id, 'record_id': '0' })
			o1 = tasks.Task(n)

		self.assertEquals(o1.values, o.values)


	def test_task_modify(self):
		"""Testing task modification"""

		o = tasks.Task({
			"name":     str(uuid.uuid4()),
			"customer": str(uuid.uuid4()),
			"rate_id":  str(uuid.uuid4()),
			"queue_id": str(uuid.uuid4()),
		})

		tasks.add(o)
		with self.assertRaises(ValueError):
			tasks.modify('abracadabra', '', {})

		with self.assertRaises(TypeError):
			tasks.modify('id', '', {'state':tasks.constants.STATE_MAXVALUE+1})

		data = {'value': 29}
		tasks.modify('id', o.base_id, data)
		with database.DBConnect(primarykey=o.base_id) as db:
			o1 = tasks.Task(db.find_one('tasks', {'base_id':o.base_id, 'record_id': '0' }))
		o.set(data)
		self.assertEquals(o1.values, o.values)


	def test_task_remove(self):
		"""Check state changing"""

		o = tasks.Task({
			"name":     str(uuid.uuid4()),
			"customer": str(uuid.uuid4()),
			"rate_id":  str(uuid.uuid4()),
			"queue_id": str(uuid.uuid4()),
		})

		tasks.add(o)
		ts = int(time.time()+10)
		tasks.remove('id', o.base_id, ts)
		o.set({'state': tasks.constants.STATE_DELETED, 'time_destroy':ts})

		with database.DBConnect(primarykey=o.base_id) as db:
			o1 = tasks.Task(db.find_one('tasks', {'base_id':o.base_id, 'record_id': '0' }))
		self.assertEquals(o1.values, o.values)


	def test_task_update(self):
		"""Check task recreating"""

		o = tasks.Task({
			"name":        str(uuid.uuid4()),
			"customer":    str(uuid.uuid4()),
			"rate_id":     str(uuid.uuid4()),
			"queue_id":    str(uuid.uuid4()),
			"time_create": int(time.time())-60
		})

		tasks.add(o)

		data = {'value': 29}
		ts = int(time.time() + 10)
		tasks.update(o.base_id, data, ts)
		with database.DBConnect(primarykey=o.base_id) as db:
			o1 = tasks.Task(db.find_one('tasks', {'base_id':o.base_id, 'record_id': '0' }))

		#Getting queues
		with database.DBConnect(primarykey=o.base_id) as db:
			nq = db.find_one('queue', {'id':o1.queue_id})
			oq = db.find_one('queue', {'id':o.queue_id})

		self.assertTrue(oq is not None)

		#Time_create is equal with time_check in new task
		self.assertEquals(o1.time_create, nq['time_check'])

		#New id's and time_create
		self.assertNotEquals(o1.queue_id, o.queue_id)
		self.assertNotEquals(o1.task_id, o.task_id)
		self.assertNotEquals(o1.time_create, o.time_create)

		#Updated data
		o.set(data)
		o1.queue_id = o.queue_id
		o1.task_id = o.task_id
		o1.time_create = o.time_create
		self.assertEquals(o1.values, o.values)

