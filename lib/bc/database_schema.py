from bc import database

class DBTable(object):
	def __init__(self, name, conn=None, options=[], columns=[], indexes=[]):
		self.columns   = []
		self.indexes   = []
		self.tableopts = []

		self.conn = conn
		self.name = name
		self.set_table_options(options)

		for o in columns:
			# ( name, type [, constraint ] )
			if len(o) < 2:
				continue
			self.columns.append(o)

		for o in indexes:
			self.add_index(o['cols'], **o.get('opts', dict()))


	def set_table_options(self, arr):
		if len(arr) > 0:
			self.tableopts.extend(arr)


	def sql_create_table(self):
		res = [ "CREATE TABLE IF NOT EXISTS" ]
		res.append(self.name)

		cols = []
		for c in self.columns:
			cols.append(' '.join(c))
		res.append('(' + ', '.join(cols) + ')')
		res.extend(self.tableopts)

		yield ' '.join(res) + ';'


	def sql_create_indexes(self):
		for idx in self.indexes:
			res = [ "CREATE" ]
			if idx['unique'] == True:
				res.append("UNIQUE")
			res.extend([ "INDEX", idx['name'] ])
			res.extend([ "ON", self.name ])
			res.extend([ "USING", idx['method'] ])
			res.append( "(" + ", ".join(idx['cols']) + ")")
			yield " ".join(res) + ";"


	def sql_drop_table(self):
		yield 'DROP TABLE IF EXISTS ' + self.name


	def sql_drop_indexes(self):
		for idx in self.indexes:
			yield 'DROP INDEX IF EXISTS ' + idx['name']


	def add_index(self, cols, name=None, method=None, unique=False):
		iner_name = []
		arr = []
		for c in cols: # ( name, sort_order )
			n = c[0]
			s = len(c) > 1 and c[1] or 'ASC'

			if s not in [ 'ASC', 'DESC' ]:
				continue

			iner_name.append(n)
			arr.append( n + ' ' + s)

		iner_name.sort()
		iner_name.insert(0, self.name)
		if unique:
			iner_name.append('unique')
		iner_name.append('index')

		self.indexes.append(
			{
				'name':   name or '_'.join(iner_name),
				'cols':   arr,
				'method': 'BTREE',
				'unique': bool(unique)
			}
		)


	def sql_create(self):
		for s in self.sql_create_table():
			yield s
		for s in self.sql_create_indexes():
			yield s


	def sql_drop(self):
		for s in self.sql_drop_indexes():
			yield s
		for s in self.sql_drop_table():
			yield s


	def create(self, conn):
		connect = conn or self.conn
		for s in self.sql_create():
			connect.execute(s)


	def drop(self, conn):
		connect = conn or self.conn
		for s in self.sql_drop():
			connect.execute(s)


SCHEMA = [
	DBTable("metrics",
			columns = [
				("id",        "varchar(128)", "NOT NULL PRIMARY KEY"),
				("type",      "varchar(32)",  "NOT NULL"),
				("formula",   "varchar(32)",  "NOT NULL"),
				("aggregate", "int",          "NOT NULL"),
			]
		),
	DBTable("queue",
			columns = [
				# A composite id of the two fields.
				("base_id",     "varchar(36)",  "NOT NULL PRIMARY KEY"),
				("record_id",   "varchar(36)",  "NOT NULL DEFAULT '0'"),

				("group_id",    "bigint",       "NOT NULL DEFAULT '0'"),

				("customer",    "varchar(36)",  "NOT NULL"),
				("rate_id",     "varchar(36)",  "NOT NULL"),
				("metric_id",   "varchar(36)",  "NOT NULL"),
				("rate",        "bigint",       "NOT NULL DEFAULT '0'"),
				("state",       "int",          "NOT NULL"),
				("value",       "bigint",       "NOT NULL"),
				("time_check",  "int",          "NOT NULL"),
				("time_create", "int",          "NOT NULL"),
				("time_destroy","int",          "NOT NULL DEFAULT '0'"),
				("target_user", "varchar(36)",  "DEFAULT ''"),
				("target_uuid", "varchar(36)",  "DEFAULT ''"),
				("target_descr","varchar(36)",  "DEFAULT ''"),
			],
			indexes = [
				{ "cols": [ ("base_id", "ASC"), ("record_id", "ASC") ], 'unique': True },
				{ "cols": [ ("group_id", "ASC") ] },
				{ "cols": [ ("state", "ASC") ] },
			]
		),
	DBTable("rates",
			columns = [
				("id",           "varchar(36)",   "NOT NULL PRIMARY KEY"),
				("description",  "varchar(1024)", "NOT NULL"),
				("metric_id",    "varchar(128)",  "NOT NULL"),
				("tariff_id",    "varchar(36)",   "NOT NULL"),
				("rate",         "bigint",        "NOT NULL"),
				("currency",     "int",           "NOT NULL"),
				("state",        "int",           "NOT NULL"),
				("time_create",  "int",           "NOT NULL"),
				("time_destroy", "int",           "NOT NULL"),
			],
			indexes = [
				{ "cols": [ ("state", "ASC"), ("metric_id", "ASC"), ("tariff_id","ASC") ] }
			]
		),
	DBTable("tariffs",
			columns = [
				("id",          "varchar(36)",   "NOT NULL PRIMARY KEY"),
				("name",        "varchar(64)",   "NOT NULL"),
				("description", "varchar(1024)", "NOT NULL"),
				("time_create", "int",           "NOT NULL"),
				("time_destroy","int",           "NOT NULL"),
				("state",       "int",           "NOT NULL"),
			],
			indexes = [
				{ "cols": [ ("state", "ASC") ] }
			]
		),
	DBTable("customers",
			columns = [
				("id",              "varchar(36)",   "NOT NULL PRIMARY KEY"),
				("login",           "varchar(64)",   "NOT NULL"),
				("name_short",      "varchar(255)",  "NOT NULL"),
				("name_full",       "varchar(1024)", "NOT NULL DEFAULT ''"),
				("comment",         "varchar(1024)", "NOT NULL DEFAULT ''"),
				("contract_client", "varchar(255)",  "NOT NULL DEFAULT ''"),
				("contract_service","varchar(255)",  "NOT NULL DEFAULT ''"),
				("tariff_id",       "varchar(36)",   "NOT NULL DEFAULT ''"),
				("contact_person",  "varchar(255)",  "NOT NULL DEFAULT ''"),
				("contact_email",   "varchar(255)",  "NOT NULL DEFAULT ''"),
				("contact_phone",   "varchar(30)",   "NOT NULL DEFAULT ''"),
				("state",           "int",           "NOT NULL DEFAULT '0'"),
				("time_create",     "int",           "NOT NULL"),
				("time_destroy",    "int",           "NOT NULL DEFAULT '0'"),
				("wallet_mode",     "int",           "NOT NULL DEFAULT '0'"),
				("wallet",          "bigint",        "NOT NULL DEFAULT '0'"),
			],
			indexes = [
				{ "cols": [ ("state", "ASC") ] }
			]
		),
	DBTable("auth",
			columns = [
				("id",    "varchar(36)",   "NOT NULL PRIMARY KEY"),
				("role",  "varchar(64)",   "NOT NULL"),
				("method","varchar(64)",   "NOT NULL"),
				("secret","varchar(1024)", "NOT NULL"),
				("host",  "varchar(255)",  "NOT NULL DEFAULT ''"),
			],
			indexes = [
				{ "cols": [ ("role", "ASC"), ("method", "ASC") ] }
			]
		),
]

def create_schema(dbname=None, dbuser=None, dbpass=None):
	with database.DBConnect(dbname=dbname, dbuser=dbuser, dbpass=dbpass, autocommit=False) as db:
		for table in SCHEMA:
			table.create(db)
		db.commit()


def destroy_schema(dbname=None, dbuser=None, dbpass=None):
	with database.DBConnect(dbname=dbname, dbuser=dbuser, dbpass=dbpass, autocommit=False) as db:
		for table in SCHEMA:
			table.drop(db)
		db.commit()

