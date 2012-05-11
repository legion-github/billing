import unithelper

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
	def test_1(self):
		test_base_creator = """
		DROP TABLE IF EXISTS `new_table`;
		CREATE TABLE `new_table` (
		`uuid` varchar(36) NOT NULL,
		`bigint` bigint(20) NOT NULL,
		`timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
		 PRIMARY KEY (`uuid`)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8;
		"""
		print database.DB().cursor().execute(test_base_creator)




