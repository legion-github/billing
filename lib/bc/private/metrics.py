#!/usr/bin/python2.6
import bobject

from bc import database


class Metric(bobject.BaseObject):
	def __init__(self, data = None):
		self.__values__ = {
			'mtype':                '',
			'count_dimention_koef': 0,
			'count_dimention_type': '',
			'time_dimention_koef':  0,
			'time_type':            0,
			'aggregate':            0,
		}

		if data:
			self.set(data)


def add(metric):
	with database.DBConnect() as db:
		db.insert('metrics', metric.values)
