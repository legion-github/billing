#!/usr/bin/python2.6

class Rate(object):
	__data = 0L

	def __init__(self, data = 0L):
		if isinstance(data, (basestring, int, long)):
			self.__data = abs(int(data))
			return

		elif isinstance(data, dict):
			ak = data.keys()
			al = len(ak) - 1
			i = 0
			for k in ak:
				self.__data += abs(int(data[k])) * 10**int(ak[al - i])
				i += 1
			return

		raise TypeError('Unsupported class type: ' + repr(type(data)))

	def export(self, units = 12, inc = 3):
		ulen  = units
		inc   = inc
		rank  = 10**inc
		units = range(0, ulen*inc, inc)

		res = {}
		x = self.__data
		for k in reversed(units):
			if k == 0:
				res[0] = x
				break
			res[k] = x % rank
			x /= rank
		return res

	def __nonzero__(self): return (self.__data != 0)

	def __int__(self):  return int(self.__data)
	def __str__(self):  return str(self.__data)
	def __repr__(self): return str(self.__data)

	def __lt__(self, other): return (self.__data <  other)
	def __le__(self, other): return (self.__data <= other)
	def __eq__(self, other): return (self.__data == other)
	def __ne__(self, other): return (self.__data != other)
	def __gt__(self, other): return (self.__data >  other)
	def __ge__(self, other): return (self.__data >= other)

	def __add__(self, other):  return Rate(self.__data + int(other))
	def __mul__(self, other):  return Rate(self.__data * int(other))

	def __radd__(self, other): return Rate(self.__data + int(other))
	def __rmul__(self, other): return Rate(self.__data * int(other))

	def __iadd__(self, other): return Rate(self.__data + abs(int(other))) 
	def __imul__(self, other): return Rate(self.__data * abs(int(other))) 

