#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '1.0'

import uuid
import time

from bc import database

from bc.private import readonly
from bc.private import bobject


class TaskConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'STATE_PROCESSING': 'processing',
		'STATE_DONE':       'done',
		'STATE_AGGREGATE':  'aggregate',
	}

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

			# Текущее состояние задания
			'state':          c.STATE_PROCESSING,

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


def add(mtype, task):
	with database.DBConnect(primarykey=task.id) as db:
		db.insert('queue', task.values)


def set_done(mtype, task):
	with database.DBConnect(primarykey=task.id) as db:
		c = TaskConstants()
		db.update('queue',
			{
				'id':    task.id,
				'state': c.STATE_PROCESSING
			},
			{
				'state': c.STATE_DONE
			}
		)
