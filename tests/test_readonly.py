import unithelper
from bc import readonly

class TestConstants(object):
	__metaclass__ = readonly.metaClass
	__readonly__  = {
		'foo': 111,
		'bar': 'XXX',
		'baz': [1,2,3]
	}

class Test(unithelper.TestCase):
	def test_readonly(self):
		"""Check readonly class"""

		with self.assertRaises(AttributeError):
			c = TestConstants()
			c.foo = 222

		with self.assertRaises(AttributeError):
			c = TestConstants()
			c.bar = 'ZZZ'

		with self.assertRaises(AttributeError):
			c = TestConstants()
			c.baz = [4,5,6]

		with self.assertNotRaises(AttributeError):
			c = TestConstants()
			c.baz.append(4)
