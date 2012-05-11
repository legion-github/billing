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
		test_base_creator = """
		DROP TABLE IF EXISTS `new_table`;
		CREATE TABLE `new_table` (
		`uuid` varchar(36) NOT NULL,
		`big` bigint(20) NOT NULL,
		`time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
		 PRIMARY KEY (`uuid`)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8;
		"""
		database.DB().cursor().execute(test_base_creator)

	def test_insertdict(self):
		dictionary = {
				'uuid': uuid.uuid4(),
				'big': 2**30,
				'time': int(time.time())
				}
		database.DB().insertdict('new_table', dictionary)






