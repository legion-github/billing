#!/usr/bin/python2.6

import time
import uuid

from c2 import mongodb


class Metric(object):
	def __init__(self, mtype = None):
		self.__dict__['values'] = {
			'mtype':           '',
			'count_dimention': {},
			'time_dimention':  {},
			'time_type':       0,
			'aggrigate':       0,
		}

		if not mtype:
			return

		o = mongodb.billing_collection('metrics').find_one({'mtype': mtype})
		if not o:
			raise ValueError('Unknown metric')
		self.set(o)


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


	def set(self, o):
		for n in self.__dict__['values'].keys():
			if n in o:
				self.__dict__['values'][n] = o[n]
		return self


	def __getattr__(self, name):
		o = self.__dict__['values']
		if name not in o:
			raise KeyError
		return o[name]


	def __setattr__(self, name, value):
		o = self.__dict__['values']
		if name not in o:
			raise KeyError

		t = type(o.get(name))

		if not isinstance(value, t):
			raise TypeError

		o[name] = value


	def __delattr__(self, name):
		raise ValueError('Operation not allowed')


	def __str__(self):
		return str(self.values)
