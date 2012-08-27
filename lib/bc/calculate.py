from bc import metrics

def calculate(task, metric):

	if task['rate'] == 0:
		return 0

	if int(task['time_destroy']) > 0:
		delta_ts = int(task['time_destroy']) - int(task['time_check'])
	else:
		delta_ts = int(task['time_now']) - int(task['time_check'])

	switch = {
		metrics.constants.FORMULA_SPEED: lambda: task['rate'] * delta_ts * task['value'],
		metrics.constants.FORMULA_TIME:  lambda: task['rate'] * delta_ts,
		metrics.constants.FORMULA_UNIT:  lambda: task['rate'] * task['value'],
	}

	return switch[metric.formula]()

