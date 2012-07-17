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
	def __init__(self, modulename, methodname, modulewithlog):
		self.__dict__.update(locals())

	def __enter__(self):
		import sys

		def foo(*args, **kwargs):
			raise Exception("Faked exception, for tests")

		def pseudolog(*args, **kwargs):
			pass

		self.logger=sys.modules[self.modulewithlog].LOG.error
		sys.modules[self.modulewithlog].LOG.error=pseudolog

		self.backup=getattr(sys.modules[self.modulename], self.methodname)
		setattr(sys.modules[self.modulename], self.methodname, foo)

		return True

	def __exit__(self, type, vaue, traceback):
		import sys
		setattr(sys.modules[self.modulename], self.methodname, self.backup)
		sys.modules[self.modulewithlog].LOG.error=self.logger


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


