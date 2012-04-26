#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '1.0'

import uuid
import time

import readonly
import bobject

class TaskConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'STATE_PROCESSING': 'processing',
		'STATE_DONE':       'done',
		'STATE_AGGREGATE':  'aggregate',
	}

constants = TaskConstants()

class Task(bobject.BaseObject):
	def __init__(self, uid = None, mtype = None):

		c = TaskConstants()
		now = int(time.time())

		self.__dict__['values'] = {
			# Уникальный идентификатор задания
			'uuid':           str(uuid.uuid4()),

			# Владелец задания, тот чей счёт используется
			'customer':       '',

			# Уникальный идентификатор правила тарифа
			'rid':            '',

			# (Дупликация) стоймость метрики в тарифе
			'rate':           '',

			# (Дупликация) описание метрики в тарифе
			'description':    '',

			# Текущее состояние задания
			'state':          c.STATE_PROCESSING,

			# Значение ресурса задания. Это может быть время или штуки
			'value':          0,

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

		if not uid or not mtype:
			return

		# TODO: Нужно будет найти сервер на котором находится mtype по uid
		o = mongodb.billing_collection(mtype).find_one({'uuid':uid})
		if not o:
			raise ValueError('Unknown task')
		self.set(o)
