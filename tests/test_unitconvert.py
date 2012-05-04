import unithelper
from bc import unitconvert


class Test(unithelper.TestCase):
	def test_parse(self):
		"""Check unit parsing"""

		for s in ['5 kilobytes', '5 KiloByte', '5kb', '5KB']:
			self.assertEqual((5000L, 'byte_decimal'), unitconvert.convert_from(s))

		for s in ['5 kibibytes', '5KiBIByte', '5kib', '5KiB']:
			self.assertEqual((5120L, 'byte_binary'), unitconvert.convert_from(s))


	def test_reverse(self):
		"""Check conversion from number to unit"""

		self.assertEqual((5L, 'KB'), unitconvert.convert_to('byte_decimal', 5000))
		self.assertEqual((4.8828125, 'KiB'), unitconvert.convert_to('byte_binary', 5000))
