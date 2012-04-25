import unittest
from bc.private import readonly

class TestConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'foo': 111,
		'bar': 'XXX',
		'baz': [1,2,3]
	}

class Test(unittest.TestCase):
	def test_readonly(self):
		"""Check readonly class"""

		def setx():
			c = TestConstants()
			c.foo = 222
		self.assertRaises(AttributeError, setx)

		def setx():
			c = TestConstants()
			c.bar = 'ZZZ'
		self.assertRaises(AttributeError, setx)

		def setx():
			c = TestConstants()
			c.baz.append(4)
		self.assertTrue(setx)
