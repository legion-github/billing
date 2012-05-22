from private.tasks import task_done
from private import metrics

def calculate(task, metric, nostate=False):
	"""
	nostate - argument for readonly actions, default=False
	"""

	if int(task.time_destroy) > 0:
		delta_ts = int(task.time_destroy) - int(task.time_check)
		if not nostate:
			task_done(task, metric)
	else:
		delta_ts = int(task.time_now) - int(task.time_check)

	if delta_ts < 0:
		delta_ts = 0

	if task.rate == 0:
		return (None, None)

	switch = {
		metrics.constants.FORMULA_SPEED: lambda: task.rate * delta_ts * task.value,
		metrics.constants.FORMULA_TIME:  lambda: task.rate * delta_ts,
		metrics.constants.FORMULA_UNIT:  lambda: task.rate * task.value,
	}

	return (task.customer, switch[metric.formula]())

