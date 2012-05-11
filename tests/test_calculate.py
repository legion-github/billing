import time
import unithelper
from bc.private import tasks
from bc.calculate import calculate
from bc.private import metrics

class Test(unithelper.TestCase):
	def test_new_task(self):
		"""Check task calculation"""

		now = int(time.time())
		delay = 40
		values = {
			'uuid':           '',
			'customer':       'customer_id',
			'rid':            '',
			'rate':           '931322574615478515625000',
			'description':    '',
			'state':          tasks.constants.STATE_PROCESSING,
			'value':          1024,
			'time_now':       now-delay,
			'time_check':     now-delay,
			'time_create':    now-delay,
			'time_destroy':   now,
			'target_user':    '',
			'target_uuid':    '',
			'target_descr':   '',
		}

		t = tasks.Task()
		t.set(values)


		metric = {
			'mtype':           '',
			'count_dimention': {},
			'time_dimention':  {},
			'time_type':       1,
			'aggrigate':       0,
		}

		m = metrics.Metric(metric)

		self.assertEqual((values['customer'], int(values['rate']) * values['value'] * delay), calculate(t, m, nostate=True))

		m.time_type=0

		self.assertEqual((values['customer'], int(values['rate']) * values['value']), calculate(t, m, nostate=True))
