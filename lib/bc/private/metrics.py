#!/usr/bin/python2.6
import bobject
import readonly

from bc import database

class TariffRateConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'TYPE_SPEED': 'speed',
		'TYPE_COUNT': 'count',
	}

constants = TariffRateConstants()

class Metric(bobject.BaseObject):
	def __init__(self, data = None):
		self.__values__ = {
			'mtype':      '',

			'count_desc': '',
			'count_unit': 0L,

			'time_desc':  '',
			'time_unit':  0L,

			'type':       0L,
			'aggregate':  0,
		}

		if data:
			self.set(data)


def add(metric):

	with database.DBConnect() as db:
		db.insert('metrics', metric.values)


def get_all():

	with database.DBConnect() as db:
		for i in db.query("SELECT * FROM `metrics` m;"):
			yield Metric(i)

