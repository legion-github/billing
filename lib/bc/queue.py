import time

from bc.private import metrics
from bc.private import tasks
from bc.calculate import calculate

from bc import database

BC_QUEUES=[]


def register_queue():
	global BC_QUEUES
	for i in metrics.get_all():
		queue = {
				'metric': i,
				'calculate': lambda task, nostate: calculate(task, i, nostate),
				'get': get_task_aggregate if i.aggregate else get_task,
		}

		BC_QUEUES.append(queue)


def get_task(name, uid, aggregate = False):
	now = int(time.time())
	task=tasks.Task()

	query = {
		'uuid': uid,
		'state': task.c.STATE_PROCESSING
	}

	action = {
		'$set': { 'time_check': now }
	}

	if aggregate:
		action['$set']['state'] = task.c.STATE_DONE
		action['$set']['time_destroy'] = now

	t = mongodb.collection('queue-' + name).find_and_modify(query, action, new = False)
	if t:
		task['time_now'] = now

	return task


def get_task_aggregate(name, uid):
	return get_task(name, uid, aggregate = True)
