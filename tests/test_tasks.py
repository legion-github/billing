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
			'base_id':        '123',
			'record_id':      '0',
			'customer':       '',
			'rid':            '',
			'state':          tasks.constants.STATE_ENABLED,
			'rate':           0L,
			'value':          0L,
			'time_check':     now,
			'time_create':    now,
			'time_destroy':   0,
			'target_user':    '',
			'target_uuid':    '',
			'target_descr':   '',
		}

		t = tasks.Task()
		t.set({'base_id':'123'})

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
			"rid":      str(uuid.uuid4()),
		})

		tasks.add(o)

		with database.DBConnect() as db:
			o1 = db.find_one('queue', {'base_id':o.base_id, 'record_id': '0' })

		self.assertEquals(tasks.Task(o1), o)

