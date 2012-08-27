#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '1.0'

import uuid
import time

from bc import database

from bc import readonly
from bc import bobject


class TaskConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'STATE_ENABLED':   1,
		'STATE_DISABLED':  2,
		'STATE_DELETED':   3,
		'STATE_PROCESSED': 4,
		'STATE_AGGREGATE': 5,
		'STATE_MAXVALUE':  6,
	}

	def import_state(self, val):
		x = {
			'enable':    self.__readonly__['STATE_ENABLED'],
			'disable':   self.__readonly__['STATE_DISABLED'],
			'delete':    self.__readonly__['STATE_DELETED'],
			'processed': self.__readonly__['STATE_PROCESSED'],
			'aggregate': self.__readonly__['STATE_AGGREGATE']
		}
		return x.get(val, None)

constants = TaskConstants()

class Task(bobject.BaseObject):
	def __init__(self, data = None):

		c = TaskConstants()
		now = int(time.time())

		self.__values__ = {
			# Уникальный идентификатор задания
			'base_id':        str(uuid.uuid4()),
			'record_id':      '0',

			'queue_id':       '',
			'group_id':       0L,

			# Владелец задания, тот чей счёт используется
			'customer':       '',

			# Уникальный идентификатор правила тарифа
			'rate_id':        '',

			# Уникальный идентификатор метрики
			'metric_id':      '',

			# (Дупликация) стоймость метрики в тарифе
			'rate':           0L,

			# Текущее состояние задания
			'state':          c.STATE_ENABLED,

			# Значение ресурса задания. Это может быть время или штуки
			'value':          0L,

			# Тайминги задания
			'time_create':    now,
			'time_destroy':   0,

			# (Опциональные) биллинговые данные, описывающие характер VALUE
			'target_user':    '',
			'target_uuid':    '',
			'target_descr':   '',
		}

		if data:
			self.set(data)


def add(params):

	# Final internal validation
	o = Task(params)

	with database.DBConnect(primarykey=o.base_id, autocommit=False) as db:
		# Create queue id
		if not o.queue_id:
			o.queue_id = str(uuid.uuid4())

		db.insert('tasks', o.values)
		db.insert('queue',
			{
				'id':         o.queue_id,
				'time_check': int(time.time())
			}
		)
		db.commit()


def modify(typ, val, params):
	"""Modify task"""

	c = TaskConstants()

	if typ not in [ 'id' ]:
		raise ValueError("Unknown type: " + str(typ))

	# Final internal validation
	o = Task(params)

	if o.state < 0 or o.state >= c.STATE_MAXVALUE:
		raise TypeError('Wrong state')

	with database.DBConnect(primarykey=val) as db:
		db.update("tasks", { 'base_id': val, 'record_id': '0' }, params)


def remove(typ, value, ts=0):
	"""Disables task"""

	c = TaskConstants()

	modify(typ, value,
		{
			'state': c.STATE_DELETED,
			'time_destroy': ts or int(time.time())
		}
	)


def update(id, params, ts=0):
	"""Recreate task"""

	with database.DBConnect(primarykey=id, autocommit=False) as db:

		ot = db.find_one('tasks',
			{ 'base_id': id, 'record_id': '0' })
		if not ot:
			return

		nt = Task(ot.values)
		nt.set(params)
		nt.queue_id = str(uuid.uuid4())

		db.update('tasks',
			{ 'base_id': id, 'record_id': '0' },
			{ 'base_id': id, 'record_id': str(uuid.uuid4()),
			  'time_destroy': ts or int(time.time()) })

		db.insert('tasks', nt.values)
		db.insert('queue',
			{
				'id':         nt.queue_id,
				'time_check': int(time.time())
			}
		)

		db.commit()
