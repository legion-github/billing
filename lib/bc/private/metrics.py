#!/usr/bin/python2.6

import time
import uuid

from c2 import mongodb


class Metric(object):
	mtype           = ''
	count_dimention = {}
	time_dimention  = {}
	time_type       = 0
	aggrigate       = 0
	values          = property(lambda self:
		{
			'mtype':           self.mtype,
			'count_dimention': self.count_dimention,
			'time_dimention':  self.time_dimention,
			'aggrigate':       self.aggrigate
		}
	)


	def __init__(self, mtype = None):
		if not mtype:
			return

		o = mongodb.billing_collection('metrics').find_one({'mtype': mtype})
		if not o:
			raise ValueError('Unknown metric')
		self.set(o)


	def set(self, o):
		for n in self.values.keys():
			if n not in o:
				continue
			self.__dict__[n] = o[n]
		return self


	def validate(self):
		if not self.mtype:
			return False

		for o in [self.time_dimension, self.count_dimension]:
			if 'name'  not in o or not isinstance(o['name'], basestring):
				return False
			if 'value' not in o or not isinstance(o['value'], int, long):
				return False
		return True


	def add(self):
		if not self.validate():
			raise ValueError('Invalid metric')

		mongodb.billing_collection('metrics').insert(self.values, safe = True)


	def __str__(self):
		return str(self.values)
