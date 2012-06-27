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
		'STATE_AGGREGATE': 4,
		'STATE_MAXVALUE':  5,
	}

	def import_state(self, val):
		x = {
			'enable':    self.__readonly__['STATE_ENABLED'],
			'disable':   self.__readonly__['STATE_DISABLED'],
			'delete':    self.__readonly__['STATE_DELETED'],
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
			'id':             str(uuid.uuid4()),

			# Владелец задания, тот чей счёт используется
			'customer':       '',

			# Уникальный идентификатор правила тарифа
			'rid':            '',

			# (Дупликация) стоймость метрики в тарифе
			'rate':           0L,

			# Текущее состояние задания
			'state':          c.STATE_ENABLED,

			# Значение ресурса задания. Это может быть время или штуки
			'value':          0L,

			# Тайминги задания
			'time_now':       now,
			'time_check':     now,
			'time_create':    now,
			'time_destroy':   0,

			# (Опциональные) биллинговые данные, описывающие характер VALUE
			'target_user':    '',
			'target_uuid':    '',
			'target_descr':   '',
		}

		if data:
			self.set(data)


def add(task):
	with database.DBConnect(primarykey=task.id) as db:
		v = {}
		v.update(task.values)
		del v['time_now']
		db.insert('queue', v)


def modify(typ, val, params):
	"""Modify customer"""

	c = TaskConstants()

	if typ not in [ 'id' ]:
		raise ValueError("Unknown type: " + str(typ))

	# Final internal validation
	o = Task(params)

	if o.state < 0 or o.state >= c.STATE_MAXVALUE:
		raise TypeError('Wrong state')

	with database.DBConnect(primarykey=val) as db:
		db.update("queue", { 'id': val }, params)


def remove(typ, value, ts=0):
	"""Disables tariff"""

	c = TaskConstants()

	if typ == 'id':
		query = { 'id': value }
	else:
		raise ValueError("Unknown value: " + str(typ))

	if ts == 0:
		ts == int(time.time())

	with database.DBConnect(primarykey=value) as db:
		db.update("queue", query,
			{
				'state': c.STATE_DELETED,
				'time_destroy': ts
			}
		)
