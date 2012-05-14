import uuid
import MySQLdb
import unittest2 as unittest
from bc import config
from bc import database


confstr = """
{
	"database": {
		"name": "testing",
		"server": "127.0.0.1",
		"user": "root",
		"pass": "qwerty"
	}
}
"""

conf = config.read(inline = confstr, force=True)


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
	try:
		database.DB()
	except MySQLdb.OperationalError:
		return False
	return True


class DBTestCase(TestCase):
	def setUp(self):
		if not haveDatabase():
			return
		database.DB().destroy_schema()
		database.DB().create_schema()


	def tearDown(self):
		if not haveDatabase():
			return
		database.DB().destroy_schema()
