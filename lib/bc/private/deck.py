#!/usr/bin/python2.6

import time
import pymongo
import uuid
import logging
import pymongo

from pymongo.errors import DuplicateKeyError
from c2 import mongodb

from c2.core import Error

from billing import utils
from billing import customers
from billing import constants as b_constants

UID          = 'uuid'
NAME         = 'queue'
CUSTOMER     = 'customer'
USER         = 'user'
TARIFF       = 'tariff'
STATE        = 'state'
TIME_CREATE  = 'time-create'
TIME_CHECK   = 'time-check'
TIME_NOW     = 'time-now' # Internal task field. Not in database
TIME_DESTROY = 'time-destroy'
DATA         = 'info'

STATE_PROCESSING = 'processing'
STATE_DONE       = 'done'
STATE_AGGREGATE  = 'aggregate'

LOCK_TIME = 5

TASK_TEMPLATE = {
	UID:          0,
	NAME:         '',
	TARIFF:       '',
	CUSTOMER:     '',
	USER:         '',
	STATE:        '',
	TIME_NOW:     0,
	TIME_CREATE:  0,
	TIME_CHECK:   0,
	TIME_DESTROY: 0,
	DATA:         {}
}


def deck_name(name):
	return 'queue-' + str(name)


def is_valid(task):
	return set(task.keys()) >= set(TASK_TEMPLATE.keys())


def create(name, uid, user_id, udata, ignore_error = False, destroy = False):
	"""Create an new object in the queue"""

	res = mongodb.billing_collection('log_accounts').find_one({ 'user': user_id })
	if not res:
		logging.getLogger("c2.billing").error("Unable to find customer by user: %s", str(user_id))
		return

	customer = customers.get(res['customer'], ignore_wallets = True)

	now = int(time.time())
	destr_time = 0

	if destroy:
		destr_time = now

	rec_id = uid or str(uuid.uuid4())

	mongodb.billing_collection('queue-' + name).insert(
		{
			'_id':        rec_id,
			UID:          rec_id,
			NAME:         name,
			TARIFF:       customer['tariff'],
			CUSTOMER:     customer['_id'],
			USER:         user_id,
			STATE:        STATE_PROCESSING,
			TIME_CREATE:  now,
			TIME_CHECK:   now,
			TIME_DESTROY: destr_time,
			DATA:        dict(udata)
		},
		safe = True
	)


def recreate(name, uid, udata, values = None):
	now = int(time.time())
	old = mongodb.billing_collection('queue-' + name).find_and_modify(
		{
			UID: uid,
			TIME_DESTROY: 0
		},
		{
			'$set': {
				UID: uid + '--' + str(uuid.uuid4()),
				TIME_DESTROY: now 
			}
		}
	)
	if old:
		if values:
			old.update(values)

		try:
			mongodb.billing_collection('queue-' + name).update(
				{
					UID: uid,
					TIME_DESTROY: 0
				},
				{
					'$set': {
						NAME:        old[NAME],
						TARIFF:      old[TARIFF],
						CUSTOMER:    old[CUSTOMER],
						USER:        old[USER],
						STATE:       STATE_PROCESSING,
						TIME_CREATE: now,
						TIME_CHECK:  now,
						DATA:        dict(udata),
					}
				},
				upsert = True,
				safe = True
			)
		except DuplicateKeyError:
			o = mongodb.billing_collection('queue-' + name).find_one({UID: uid})
			if set(['_id', UID, TIME_DESTROY]) == set(o.keys()):
				mongodb.billing_collection('queue-' + name).remove(o)
		return True
	else:
		return False


def recreate_forever(*args, **kwargs):
	for i in xrange(0, 10):
		if recreate(*args, **kwargs):
			return
		time.sleep(1)
	raise Error("Unable to recreate object: args = {0}, kwargs = {1}".format(repr(args), repr(kwargs)))


def aggregate_daily(task, id_data = [], more = {}, remove = False):
	"""Creates/updates aggregate task"""

	time_create  = task[TIME_CREATE] // 86400 * 86400
	time_destroy = time_create + 86400

	aggr_id = utils.sha1(time_create, *id_data)

	data = {
		'$set': {
			NAME:         task[NAME],
			TARIFF:       task[TARIFF],
			CUSTOMER:     task[CUSTOMER],
			USER:         task[USER],
			STATE:        STATE_AGGREGATE,
			TIME_CREATE:  time_create,
			TIME_DESTROY: time_destroy,
			TIME_CHECK:   0,
		}
	}
	utils.dict_merge(data, more)

	mongodb.billing_collection('queue-' + task[NAME]).update(
		{ UID: aggr_id }, data,
		upsert = True,
		safe = True,
	)

	if remove:
		mongodb.billing_collection('queue-' + task[NAME]).remove(
			{ UID: task[UID] },
			safe = True,
		)


def customer_change_tariff(customer_id, tariff_id_old, tariff_id_new):
	query = {
		CUSTOMER: customer_id,
		TARIFF: tariff_id_old,
		STATE: STATE_PROCESSING,
		TIME_DESTROY: 0,
	}

	fields = [ UID, USER, DATA ]

	for name in b_constants.BC_QUEUES:
		for o in mongodb.billing_collection('queue-' + name).find(query, fields):
			recreate(name, o[UID], o[DATA],
				{
					TARIFF: tariff_id_new
				}
			)


def count_all(query):
	num = 0
	for name in b_constants.BC_QUEUES:
		num += mongodb.billing_collection('queue-' + name).find(query).count()
	return num


def save(task):
	"""Method save the object in the queue."""
	mongodb.billing_collection('queue-' + task[NAME]).save(task, safe = True)


def find_tasks(name, from_time = 0, to_time = None, fields = None, limit = None):
	if not to_time:
		to_time = int(time.time()) - LOCK_TIME
	now = int(time.time())

	return mongodb.billing_collection('queue-' + name).find(
		{
			STATE:      STATE_PROCESSING,
			TIME_CHECK: {
				'$gte': from_time,
				'$lt':  to_time
			}
		},
		sort = [ ( TIME_CHECK, pymongo.ASCENDING ) ],
		fields = fields,
		limit = limit
	)


def get_task(name, uid, remove = False):
	now = int(time.time())

	query = {
		UID: uid,
		STATE: STATE_PROCESSING
	}

	action = {
		'$set': { TIME_CHECK: now }
	}

	if remove:
		action['$set'][STATE] = STATE_DONE
		action['$set'][TIME_DESTROY] = now

	task = mongodb.billing_collection('queue-' + name).find_and_modify(query, action, new = False)
	if task:
		task[TIME_NOW] = now

	return task


def get_task_remove(name, uid):
	return get_task(name, uid, remove = True)


def get(name, from_time = 0, to_time = None, remove = False):
	"""Method receives the object from the queue, if necessary, delete it."""

	if not to_time:
		to_time = int(time.time()) - LOCK_TIME
	now = int(time.time())

	action = {
		'$set': { TIME_CHECK: now }
	}

	if remove:
		action['$set'][STATE] = STATE_DONE
		action['$set'][TIME_DESTROY] = now

	return mongodb.billing_collection('queue-' + name).find_and_modify(
		{
			TIME_CHECK: {
				'$gte': from_time,
				'$lt':  to_time
			},
			STATE:      STATE_PROCESSING
		},
		action,
		sort = { TIME_CHECK: pymongo.ASCENDING },
		new = False
	)


def get_remove(name, from_time = 0, to_time = None):
	return get(name, from_time, to_time, True)


def remove(task, remove = False):
	delete(task[NAME], task[UID], remove)


def delete(name, uid, remove = False):
	"""Removes task from the queue or mark task as deleted"""

	if remove:
		mongodb.billing_collection('queue-' + name).remove(
			{
				UID: uid,
			},
			safe = True)
		return

	mongodb.billing_collection('queue-' + name).update(
		{
			UID: uid,
			TIME_DESTROY: 0,
		},
		{
			'$set': {
				TIME_DESTROY: int(time.time())
			}
		},
		upsert = True)


def size(name):
	return mongodb.billing_collection('queue-' + name).find().count()


def cleanup(uid, field = CUSTOMER):
	for name in b_constants.BC_QUEUES:
		mongodb.billing_collection('queue-' + name).remove({ field: uid }, safe = True)


def state_done(task):
	mongodb.billing_collection('queue-' + task[NAME]).update(
		{ UID: task[UID] },
		{ '$set': { STATE: STATE_DONE } }
	)
