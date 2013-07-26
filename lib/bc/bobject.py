#!/usr/bin/python
#
# bobject.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
# Copyright (c) 2012-2013 by Nikolay Ivanov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#

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

			self.__assign(n, o[n])

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
		if name == '__values__':
			if '__values__' not in self.__dict__:
				self.__dict__['__values__'] = {}
			for k,v in value.iteritems():
				if isinstance(v, int):
					self.__dict__['__values__'][k] = long(v)
				else:
					self.__dict__['__values__'][k] = v
			return

		if name in ['__getter__', '__setter__']:
			self.__dict__[name] = value
			return

		o = self.__values__
		h = self.__setter__

		if name not in o:
			raise KeyError

		if h and name in h:
			h[name](name, value)
			return

		self.__assign(name, value)


	def __delattr__(self, name):
		raise ValueError('Operation not allowed')


	def __str__(self):
		return str(self.values)


	def __eq__(self, over):
		return self.values == over.values


	def __ne__(self, over):
		return self.values != over.values


	def __hash__(self):
		return hash((self.values[key] for key in sorted(self.values.iterkeys())))


	def __assign(self, name, value, check=True):
		o = self.__values__

		if check:
			t = typ = type(o[name])

			if typ in [ int, long ]: t = (int,long)
			elif typ == unicode:     t = (basestring,unicode)

			if not isinstance(value, t):
				raise TypeError("Type of {0} is {1}, not {2}".format(name, typ, type(value)))

		if isinstance(value, int):
			o[name] = long(value)
		elif isinstance(value, str):
			o[name] = unicode(value)
		else:
			o[name] = value
