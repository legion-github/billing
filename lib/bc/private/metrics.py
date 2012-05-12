#!/usr/bin/python2.6
import bobject

from bc.database import DB


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

	DB().insertdict('metrics', metric.values)


