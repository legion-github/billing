import time
import unithelper
import random
from bc.calculate import calculate
from bc import metrics
from bc import tasks

class Test(unithelper.TestCase):
	def setUp(self):
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

		self.metric.set({'formula': metrics.constants.FORMULA_TIME})
		self.assertEqual(
				int(values['rate']) * delay,
				calculate(values, self.metric)
		)

		self.metric.set({'formula': metrics.constants.FORMULA_UNIT})
		self.assertEqual(
				int(values['rate']) * values['value'],
				calculate(values, self.metric)
				)

		self.metric.set({'formula': metrics.constants.FORMULA_SPEED})
		self.assertEqual(
				int(values['rate']) * values['value']* delay,
				calculate(values, self.metric)
				)

		values['time_create'] = now-3*3*3*delay

		self.metric.set({'formula': metrics.constants.FORMULA_TIME})
		self.assertEqual(
				int(values['rate']) * delay,
				calculate(values, self.metric)
		)

		self.metric.set({'formula': metrics.constants.FORMULA_UNIT})
		self.assertEqual(
				int(values['rate']) * values['value'],
				calculate(values, self.metric)
				)

		self.metric.set({'formula': metrics.constants.FORMULA_SPEED})
		self.assertEqual(
				int(values['rate']) * values['value']* delay,
				calculate(values, self.metric)
				)


