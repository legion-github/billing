import unittest2 as unittest

class _AssertNotRaisesContext(object):
	"""A context manager used to implement TestCase.assertNotRaises method."""

	def __init__(self, expected, test_case):
		self.expected = expected
		self.failureException = test_case.failureException


	def __enter__(self):
		return self


	def __exit__(self, exc_type, exc_value, tb):
		if not exc_type:
			return True

		if issubclass(exc_type, self.expected):
			return False

		# let unexpected exceptions pass through
		try:
			exc_name = self.expected.__name__
		except AttributeError:
			exc_name = str(self.expected)

		raise self.failureException("%s raised" % (exc_name,))


class TestCase(unittest.TestCase):
	def __str__(self):
		return ""

	def assertNotRaises(self, excClass, callableObj=None, *args, **kwargs):

		if callableObj is None:
			return _AssertNotRaisesContext(excClass, self)

		try:
			callableObj(*args, **kwargs)
		except excClass:
			if hasattr(excClass,'__name__'):
				excName = excClass.__name__
			else:
				excName = str(excClass)
			raise self.failureException, "%s raised" % excName
