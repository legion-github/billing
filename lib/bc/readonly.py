#!/usr/bin/python
#
# readonly.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#

class metaClass(type):
	def __new__(cls, cname, bases, cdict):
		def __getmethod(attr):
			return lambda self: self.__readonly__[attr]

		for name in cdict.get('__readonly__', {}).keys():
			cdict[name] = property(__getmethod(name))

		return type.__new__(cls, cname, bases, cdict)
