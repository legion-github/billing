import sys

sys.path.insert(0, '../lib')

import unittest2 as unittest
from bc import config
from bc import database
from bc import database_schema


confstr = """
{
	"database": {
		"name": "testing",
		"server": "127.0.0.1",
		"user": "root",
		"pass": "qwerty",
		"shards": ["127.0.0.1"]
	}
}
"""

config.read(inline = confstr, force=True)


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


def haveDatabase():
	return True


class DBTestCase(TestCase):
	def setUp(self):
		if not haveDatabase():
			return
		database_schema.destroy_schema()
		database_schema.create_schema()


	def tearDown(self):
		if not haveDatabase():
			return
		database_schema.destroy_schema()


class mocker(object):
	"""
	Object for hacking preloaded objects inplace, in import tree
	"""

	def __init__(self, targets=[]):
		self.__targets = targets

	@staticmethod
	def __mocker(q):

		import sys
		path = q[0].split('.')
		preans = reduce( getattr, path[1:-1], sys.modules[path[0]])
		ans = getattr(preans, path[-1])
		setattr(preans, path[-1], q[1])
		return (q[0], ans)

	def __enter__(self):

		self.__backup = map(self.__mocker, self.__targets)

	def __exit__(self, type, vaue, traceback):
		for i in self.__backup:
			self.__mocker(i)

	@staticmethod
	def exception(*args, **kwargs):
		raise Exception("Faked exception")

	@staticmethod
	def passs(*args, **kwargs):
		pass



def requestor(dictionary, state):
	if state == 'error':
		dictionary['status']=state
		return ((01 << 1), 'InvalidRequest', dictionary)
	elif state == 'servererror':
		dictionary['status']='error'
		return ((01 << 1), 'ServerError', dictionary)
	elif state == 'ok':
		dictionary['status']=state
		return ((01 << 2), dictionary)

class hashable_dict(dict):
	def __hash__(self):
		return hash((self[key] for key in sorted(self.iterkeys())))


