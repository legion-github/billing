__version__ = '1.0'

__all__ = [ 'ValidError', 'Validate' ]

import json

class ValidError(Exception):
	"""The base class for all exceptions that Validate throws."""

	def __init__(self, value, error, *args):
		self.code  = "InvalidValue"
		self.value = value
		self.message = unicode(error).format(*args) if len(args) else unicode(str(error))
		Exception.__init__(self, self.message)


	def __str__(self):
		return "{0}: {1}".format(self.value, self.message)


	def to_json(self):
		return json.dumps({
			'code':    self.code,
			'value':   self.value,
			'message': self.message
		})

class Validate(object):
	""" Validate - class for data validation. """

	def __init__(self, arg,
			required=True,
			unknown=False,
			default=None,
			variants=None,
			min=None,
			max=None):
		"""
		Example:

		from validator import Validate as V
		tmpl = V({
		   'a': V(int),             # field 'a' required and integer.
		   'b': V(int, default=12)  # 'b' is required, but default value
		                            # is 12 if not defined.
		   'c': V({                           # 'c' is dict within two fields
		        'c1': V(int),
		        'c2': V(basestring)
		      }, required=False),             # 'c' not required.
		   'd': V([ V(int, min=2, max=10) ]), # 'd' is list of integers
		                                      # that in range 2 < d[i] < 10
		   'e': V( (V(int), V(basestring)) )  # 'e' may be integer or string
		})
		"""
		self.arg = arg
		self.default = default
		self.required = bool(required)
		self.unknown = bool(unknown)
		self.variants = variants
		self.min = min
		self.max = max
		self.path = ['Object']
		self.vtype = 'value'

		if isinstance(arg, dict) and arg:
			self.vtype = 'dict'
		if isinstance(arg, list) and arg:
			self.vtype = 'list'
		if isinstance(arg, tuple) and arg:
			self.vtype = 'tuple'


	def _check_type(self, typ):
		if typ in [ int, long ]:
			t = (int,long)
		elif typ == unicode:
			t = (basestring,unicode)
		else:
			t = typ

		if not isinstance(self.value, t):
			raise ValidError(self.curname, "Wrong type")


	def _check_variants(self, path, val):
		if self.variants != None and val not in self.variants:
			raise ValidError(path, "Unexpected value")


	def _check_ignore(self):
		if self.value == None:
			if self.required:
				raise ValidError(self.curname, "Required but not defined")
			return True
		return False


	def _check_maxmin(self, arg):
		e = None
		if isinstance(arg, (basestring, list, dict)):
			if self.min != None and self.min > len(arg): e = "short"
			if self.max != None and self.max < len(arg): e = "long"
		if isinstance(arg, (int, long)):
			if self.min != None and self.min > arg: e = "short"
			if self.max != None and self.max < arg: e = "long"
		if e:
			raise ValidError(self.curname, "Value is too {0}", e)


	def _process_value(self):
		self._check_type(self.arg)
		self._check_variants(self.curname, self.value)
		return self.value


	def _process_tuple(self):
		i = 0
		for o in self.arg:
			try:
				o.path = self.path[:-1]
				o.path.append(self.path[-1] + '[' +  str(i) + ']')
				return o.check(self.value)
			except ValidError, err:
				pass
			i += 1
		raise err


	def _process_list(self):
		self._check_type(list)
		res = []
		i = 0
		while i < len(self.value):
			o = self.arg[-1]
			if i < len(self.arg):
				o = self.arg[i]
			o.path = self.path[:-1]
			o.path.append(self.path[-1] + '[' +  str(i) + ']')

			self._check_variants(o.path, self.value[i])

			res.append(o.check(self.value[i]))
			i += 1
		return res


	def _process_dict(self):
		self._check_type(dict)
		res = {}
		for k,o in self.arg.iteritems():
			val = self.value.get(k, None)

			o.path = self.path[:]
			o.path.append(k)

			self._check_variants(o.path, val)

			res[k] = o.check(val)

		if self.unknown:
			for k,o in self.value.iteritems():
				if k in self.arg:
					continue

				path = self.path[:]
				path.append(k)

				self._check_variants(path, o)

				res[k] = o
		return res


	def check(self, *arg):
		"""
		Checks the data by current template and returns valid structure.

		Usage:
		python> tmpl = Validate( {'a': Validate(int) } )
		python> tmpl.check( {'a':1} )
		python> tmpl.check( {'a':2,'b':3} )
		"""
		self.value = arg[0]
		if self.value == None and self.default != None:
			self.value = self.default
		self.curname = ".".join(self.path)

#		print "Check", self.curname, 'type:', self.vtype

		if self._check_ignore():
			return None
		self._check_maxmin(self.value)

		return getattr(self, '_process_' + self.vtype)()
