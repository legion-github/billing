#!/usr/bin/python

__version__ = '1.0'

class BaseObject(object):

	def set(self, o):
		for n in self.__dict__['values'].keys():
			if n not in o:
				continue

			typ = type(self.__dict__['values'][n])

			if not isinstance(o[n], typ):
				raise TypeError

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

		typ = type(o.get(name))

		if not isinstance(value, typ):
			raise TypeError

		o[name] = value


	def __delattr__(self, name):
		raise ValueError('Operation not allowed')


	def __str__(self):
		return str(self.values)
