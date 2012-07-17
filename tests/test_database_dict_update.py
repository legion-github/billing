import unithelper

import unittest2 as unittest
from bc import database
from bc.database import sqlcmd


class Test(unithelper.DBTestCase):
	@unittest.skipUnless(unithelper.haveDatabase(), True)
	def test_short_form(self):
		"""Check short form syntax for SET statment in UPDATE"""

		testList = [
			(
				{ 'a': 1, 'b': 2, 'c': 3 },
				"a='1' , b='2' , c='3'"
			),
		]
		with database.DBConnect() as db:
			for m,s in testList:
				self.assertEqual(s, sqlcmd(db.sql_update(m, True)))


	@unittest.skipUnless(unithelper.haveDatabase(), True)
	def test_simple_ops(self):
		"""Check simple operation syntax for SET statment in UPDATE"""

		testList = [
			(
				{ '$inc': { 'a': 1, 'b': -2 } },
				"a=a+1 , b=b+-2"
			),
			(
				{ '$dec': { 'a': 1, 'b': -2 } },
				"a=a-1 , b=b--2"
			),
			(
				{ '$set': { 'a': 1, 'b': -2, 'c': 'C' } },
				"a=1 , b=-2 , c='C'"
			),
			(
				{ '$div': { 'a': 1, 'b': -2 } },
				"a=a/1 , b=b/-2"
			),
			(
				{ '$mult': { 'a': 1, 'b': -2 } },
				"a=a*1 , b=b*-2"
			),
		]
		with database.DBConnect() as db:
			for m,s in testList:
				self.assertEqual(s, sqlcmd(db.sql_update(m, True)))


	@unittest.skipUnless(unithelper.haveDatabase(), True)
	def test_concat(self):
		"""Check CONCAT syntax for SET statment in UPDATE"""

		testList = [
			(
				{ '$concat': { 'a': 1, 'b': 'BBB' } },
				"a=CONCAT(a,'1') , b=CONCAT(b,'BBB')"
			),
		]
		with database.DBConnect() as db:
			for m,s in testList:
				self.assertEqual(s, sqlcmd(db.sql_update(m, True)))


	@unittest.skipUnless(unithelper.haveDatabase(), True)
	def test_bit(self):
		"""Check $bit syntax for SET statment in UPDATE"""

		testList = [
			(
				{ '$bit': { 'a': { 'and': 2 } } },
				"a=a&2"
			),
			(
				{ '$bit': { 'a': { 'or': 2 } } },
				"a=a|2"
			),
			(
				{ '$bit': { 'a': { 'xor': 2 } } },
				"a=a^2"
			),
			(
				{ '$bit': { 'a': { 'rshift': 2 } } },
				"a=a>>2"
			),
			(
				{ '$bit': { 'a': { 'lshift': 2 } } },
				"a=a<<2"
			),
		]
		with database.DBConnect() as db:
			for m,s in testList:
				self.assertEqual(s, sqlcmd(db.sql_update(m, True)))


	@unittest.skipUnless(unithelper.haveDatabase(), True)
	def test_field(self):
		"""Check $field syntax for SET statment in UPDATE"""

		testList = [
			(
				{ '$inc': { 'table.a': { '$field': 'table.b' } } },
				"table.a=table.a+table.b"
			),
			(
				{ '$set': { 'table.a': { '$field': 'table.b' } } },
				"table.a=table.b"
			),
		]
		with database.DBConnect() as db:
			for m,s in testList:
				self.assertEqual(s, sqlcmd(db.sql_update(m, True)))


	@unittest.skipUnless(unithelper.haveDatabase(), True)
	def test_subfunc(self):
		"""Check substitution syntax for SET statment in UPDATE"""

		testList = [
			(
				{ '$inc': { 'a': { '$crc32': { '$abs': { '$floor': -1.5 } } } } },
				"a=a+CRC32(ABS(FLOOR(-1.5)))"
			),
			(
				{ '$set': { 'a': { '$crc32': { '$abs': { '$floor': -1.5 } } } } },
				"a=CRC32(ABS(FLOOR(-1.5)))"
			),
			(
				{ '$set': { 'a': { '$crc32': { '$abs': { '$floor': 'XXX' } } } } },
				"a=CRC32(ABS(FLOOR('XXX')))"
			),
		]
		with database.DBConnect() as db:
			for m,s in testList:
				self.assertEqual(s, sqlcmd(db.sql_update(m, True)))
