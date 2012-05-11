from private.tasks import task_done
from private.rate import Rate

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

	cost = Rate(0)

	rate = task.rate

	if rate == 0:
		return (None, None)

	
	if metric.time_type == 1:
		cost += rate * delta_ts * task.value
	elif metric.time_type == 0:
		cost += rate * task.value

	return (task.customer, cost)

