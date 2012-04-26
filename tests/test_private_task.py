import time
import unittest
from bc.private import task

class Test(unittest.TestCase):
	def test_new_task(self):
		"""Check task creation"""

		now = int(time.time())
		values = {
			'uuid':           '123',
			'customer':       '',
			'rid':            '',
			'rate':           '',
			'description':    '',
			'state':          task.constants.STATE_PROCESSING,
			'value':          0,
			'time_now':       now,
			'time_check':     now,
			'time_create':    now,
			'time_destroy':   0,
			'target_user':    '',
			'target_uuid':    '',
			'target_descr':   '',
		}

		t = task.Task()
		t.set({'uuid':'123'})

		self.assertEqual(set(t.values.keys()), set(values.keys()))
		self.assertEqual(set(t.values.values()), set(values.values()))


	def test_change_task(self):
		"""Check task modification"""

		t = task.Task()

		def setx():
			t.uuid = 123
		self.assertRaises(TypeError, setx)

		def setx():
			t.zzz = 1
		self.assertRaises(KeyError, setx)

		def setx():
			del t.zzz
		self.assertRaises(ValueError, setx)

		def setx():
			t.values = {}
		self.assertRaises(KeyError, setx)

		def setx():
			t.uuid = '123'
		self.assertTrue(setx)

		def setx():
			t.values['uuid'] = '123'
		self.assertTrue(setx)
