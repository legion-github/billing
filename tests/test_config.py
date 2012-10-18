import unithelper
import json

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

		conf_old = json.dumps(config.read())

		with self.assertNotRaises(SyntaxError):
			conf_new = config.read(inline = confstr, force=True)

		config.read(inline = conf_old, force=True)


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
		conf_old = json.dumps(config.read())
		with self.assertNotRaises(SyntaxError):
			conf = config.read(inline = confstr, force=True)
		self.assertEqual(conf['logging']['level'], 'error')

		config.read(inline = conf_old, force=True)


	def test_inline_wrong(self):
		"""Check wrong syntax in inline configuration"""

		confstr = """
		{
			"database": {
				"name": "testing
			}
		}
		"""
		conf_old = json.dumps(config.read())
		with self.assertRaises(SyntaxError):
			conf = config.read(inline = confstr, force=True)

		config.read(inline = conf_old, force=True)


	def test_file_config(self):
		"""Check reading config file"""

		conf_old = json.dumps(config.read())

		with self.assertNotRaises(SyntaxError):
			conf = config.read('./test_config1.conf', force=True)

		config.read(inline = conf_old, force=True)


	def test_file_wrong(self):
		"""Check reading config file with wrong syntax"""

		conf_old = json.dumps(config.read())
		with self.assertRaises(SyntaxError):
			conf = config.read('./test_config2.conf', force=True)

		config.read(inline = conf_old, force=True)
