import unithelper

from bc import config


class Test(unithelper.TestCase):
	def test_inline_config(self):
		"""Check reading configuration from string"""

		confstr = """
		{
			"database": {
				"name": "testing",
				"server": "127.0.0.1",
				"shards": ["127.0.0.10", "127.0.0.11", "127.0.0.12", "127.0.0.13", "127.0.0.14"]
			}
		}
		"""

		with self.assertNotRaises(ValueError):
			conf = config.read(inline = confstr, force=True)


	def test_incomplete_config(self):
		"""Check reading incomplete configuration"""

		confstr = """
		{
			"database": {
				"name": "testing",
				"server": "127.0.0.1"
			}
		}
		"""
		with self.assertNotRaises(ValueError):
			conf = config.read(inline = confstr, force=True)
		self.assertEqual(conf['logging']['level'], 'error')


	def test_inline_wrong(self):
		"""Check wrong syntax in inline configuration"""

		confstr = """
		{
			"database": {
				"name": "testing
			}
		}
		"""

		with self.assertRaises(ValueError):
			conf = config.read(inline = confstr, force=True)


	def test_file_config(self):
		"""Check reading config file"""

		with self.assertNotRaises(ValueError):
			conf = config.read('./test_config1.conf', force=True)


	def test_file_wrong(self):
		"""Check reading config file with wrong syntax"""

		with self.assertRaises(ValueError):
			conf = config.read('./test_config2.conf', force=True)
