import time
import unithelper
import random
from bc.calculate import calculate
from bc import metrics
from bc import tasks

class Test(unithelper.TestCase):
	def setUp(self):
		self.values = {
			'id':             '123',
			'customer':       'qq',
			'state':          tasks.constants.STATE_ENABLED,
		}
		self.task = tasks.Task(self.values)
		self.metric = metrics.Metric()

	def test_destroyed_task(self):
		"""Check destroyed task calculation, with checktime in start"""

		now   = int(time.time())
		delay = random.randint(10, 1000)

		values = {
			'rate':           random.randint(10**4, 10**10),
			'value':          random.randint(10**4, 10**10),
			'time_check':     now-delay,
			'time_create':    now-delay,
			'time_destroy':   now,
		}
		self.task.set(values)

		self.metric.set({'formula': metrics.constants.FORMULA_TIME})
		self.assertEqual(
				(self.values['customer'], int(values['rate']) * delay),
				calculate(self.task, self.metric, nostate=True)
		)

		self.metric.set({'formula': metrics.constants.FORMULA_UNIT})
		self.assertEqual(
				(self.values['customer'], int(values['rate']) * values['value']),
				calculate(self.task, self.metric, nostate=True)
				)

		self.metric.set({'formula': metrics.constants.FORMULA_SPEED})
		self.assertEqual(
				(self.values['customer'], int(values['rate']) * values['value']* delay),
				calculate(self.task, self.metric, nostate=True)
				)

		self.task.set({'time_create': now-3*3*3*delay})

		self.metric.set({'formula': metrics.constants.FORMULA_TIME})
		self.assertEqual(
				(self.values['customer'], int(values['rate']) * delay),
				calculate(self.task, self.metric, nostate=True)
		)

		self.metric.set({'formula': metrics.constants.FORMULA_UNIT})
		self.assertEqual(
				(self.values['customer'], int(values['rate']) * values['value']),
				calculate(self.task, self.metric, nostate=True)
				)

		self.metric.set({'formula': metrics.constants.FORMULA_SPEED})
		self.assertEqual(
				(self.values['customer'], int(values['rate']) * values['value']* delay),
				calculate(self.task, self.metric, nostate=True)
				)


