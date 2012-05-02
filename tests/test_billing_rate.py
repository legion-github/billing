import unithelper
from bc.private.rate import Rate

class Test(unithelper.TestCase):
	def test_init_from_string(self):
		"""Check init from string"""
		self.assertEquals(1, Rate('1'))
		self.assertEquals(1, Rate('0000001'))
		self.assertEquals(100000000000900800700600500400300200100, Rate('100000000000900800700600500400300200100'))
		self.assertRaises(ValueError, lambda: Rate('1.0'))

	def test_init_from_num(self):
		"""Check init from number"""
		self.assertEquals(1, Rate(1))
		self.assertEquals(1000, Rate(1000))
		self.assertEquals(1000, Rate(1000L))
		self.assertRaises(TypeError, lambda: Rate(1.0))

	def test_arithmetic(self):
		"""Check arithmetic operations"""
		r = Rate(2)
		self.assertEquals(4, r + r)
		self.assertEquals(3, r + 1)
		self.assertEquals(3, 1 + r)

		self.assertEquals(4, r + 2.5)
		self.assertEquals(4, 2.5 + r)

		self.assertEquals(4, 2 * r)
		self.assertEquals(4, r * 2)

		r *= 2
		self.assertEquals(4, r)

	def test_unsupported_arithmetic(self):
		"""Check unsupported operations"""
		r = Rate(4)
		self.assertRaises(TypeError, lambda: r / 2)
		self.assertRaises(TypeError, lambda: r - 2)
		self.assertRaises(TypeError, lambda: 8 / r)
		self.assertRaises(TypeError, lambda: 8 - r)

	def test_export(self):
		"""Check export to dict()"""
		r = Rate(100000000000900800700600500400300200100)

		good = {0:100000L, 3:0L, 6:0L, 9:900L, 12:800L, 15:700L, 18:600L, 21:500L, 24:400L, 27:300L, 30:200L, 33:100L}
		self.assertEquals(good, r.export())

		good = {0:100000000000900800700600500L, 9:200L, 3:400L, 12:100L, 6:300L}
		self.assertEquals(good, r.export(units = 5))

		good = {0:100000000000900L, 6:800700L, 12:600500L, 18:400300L, 24:200100L}
		self.assertEquals(good, r.export(units = 5, inc = 6))
