#!/usr/bin/python2.6
import bobject
import readonly

from bc import database

class MetricConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'FORMULA_SPEED': 'speed',
		'FORMULA_TIME':  'time',
		'FORMULA_UNIT':  'unit',
	}

constants = MetricConstants()

class Metric(bobject.BaseObject):
	def __init__(self, data = None):
		self.__values__ = {
			'id':         u'',
			'type':       u'',
			'formula':    u'',
			'aggregate':  0,
		}

		if data:
			self.set(data)


def add(metric):
	"""Creates new billing metric"""

	with database.DBConnect() as db:
		r = db.find_one('metrics', { 'id': metric.id })
		if not r:
			db.insert('metrics', metric.values)


def get_all():
	"""Returns all metrics"""

	with database.DBConnect() as db:
		for i in db.find('metrics'):
			yield Metric(i)


def get(mid):
	"""Returns metric by id or None if metric not found"""

	with database.DBConnect() as db:
		r = db.find_one('metrics', { 'id': mid })
		if r:
			return Metric(r)
		return None
