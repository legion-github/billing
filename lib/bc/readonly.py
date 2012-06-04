#!/usr/bin/python2.6

class metaClass(type):
	def __new__(cls, cname, bases, cdict):
		def __getmethod(attr):
			return lambda self: self.__readonly__[attr]

		for name in cdict.get('__readonly__', {}).keys():
			cdict[name] = property(__getmethod(name))

		return type.__new__(cls, cname, bases, cdict)
