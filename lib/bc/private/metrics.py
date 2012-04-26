#!/usr/bin/python2.6

import time
import uuid

import bobject

from c2 import mongodb


class Metric(bobject.BaseObject):
	def __init__(self, data = None):
		self.__dict__['values'] = {
			'mtype':           '',
			'count_dimention': {},
			'time_dimention':  {},
			'time_type':       0,
			'aggrigate':       0,
		}

		if data:
			self.set(data)


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
		# XXXlegion: Wrong place for database operations ?
		if not self.validate():
			raise ValueError('Invalid metric')

		mongodb.billing_collection('metrics').insert(self.values, safe = True)


