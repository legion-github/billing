#!/usr/bin/python2.6
import bobject

from bc import database


class Metric(bobject.BaseObject):
	def __init__(self, data = None):
		self.__values__ = {
			'mtype':                '',
			'count_dimention_koef': 0L,
			'count_dimention_type': '',
			'time_dimention_koef':  0L,
			'time_type':            0L,
			'aggregate':            0,
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

