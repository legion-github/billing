import unithelper
import uuid
import time

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

class Test(unithelper.TestCase):
	def setUp(self):
		test_base_dropper = """
		DROP TABLE IF EXISTS `new_table`;
		"""
		test_base_creator="""
		CREATE TABLE `new_table` (
		`uuid` varchar(36) NOT NULL,
		`big` bigint(20) NOT NULL,
		`time` int(11) NOT NULL,
		 PRIMARY KEY (`uuid`)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8;
		"""
		c = database.DB().cursor()
		c.execute(test_base_dropper)

		c.execute(test_base_creator)
		database.DB().conn.commit()

	def test_insertdict(self):
		"""
		insertdict test
		"""
		dictionary = {
				'uuid': str(uuid.uuid4()),
				'big': 2**32,
				'time': int(time.time())
				}
		database.DB().insertdict('new_table', dictionary)
		c = database.DB().cursor()
		c.execute("SELECT * FROM `new_table` WHERE `uuid`='{0}';".format(dictionary['uuid']))
		self.assertEqual(dictionary, c.fetchone())






