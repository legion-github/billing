#!/usr/bin/python

__version__ = '1.0'

class BaseObject(object):
	__values__ = {}
	__getter__ = {}
	__setter__ = {}

	def set(self, o):
		h = self.__setter__

		for n in self.__values__.keys():
			if n not in o:
				continue

			if h and n in h:
				h[n](n, o[n])
				continue

			if o[n] == None:
				continue

			typ = type(self.__values__[n])

			if not isinstance(o[n], typ):
				raise TypeError("Type of {0} is {1}, not {2}".format(o[n], type(o[n]),typ))

			self.__values__[n] = o[n]

		return self


	def __getattr__(self, name):
		if name == 'values':
			return self.__values__

		o = self.__values__
		h = self.__getter__

		if name not in o:
			raise KeyError

		if h and name in h:
			return h[name](name)

		return o[name]


	def __setattr__(self, name, value):
		if name in ['__values__', '__getter__', '__setter__']:
			self.__dict__[name] = value
			return

		o = self.__values__
		h = self.__setter__

		if name not in o:
			raise KeyError

		if h and name in h:
			h[name](name, value)
			return

		typ = type(o.get(name))

		if not isinstance(value, typ):
			raise TypeError

		o[name] = value


	def __delattr__(self, name):
		raise ValueError('Operation not allowed')


	def __str__(self):
		return str(self.values)


	def __eq__(self, over):
		return self.values == over.values


	def __ne__(self, over):
		return self.values != over.values
