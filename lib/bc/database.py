import time
import uuid
import MySQLdb
from MySQLdb import cursors

import config
import hashing

class DBError(Exception):
	"""The base class for database exceptions that our code throws"""

	def __init__(self, error, *args):
		Exception.__init__(self, unicode(error).format(*args) if len(args) else unicode(str(error)))


def get_host(key=None):
	"""Returns database server"""

	conf = config.read()

	if isinstance(key, basestring):
		ring = hashing.HashRing(conf['database']['shards'])
		host = ring.get_node(key)
	else:
		host = conf['database']['server']

	return host


def _runtime_decorator(obj, n):
	def x(*args, **kwargs):
		return obj._call_parent(getattr(super(obj.__class__, obj), n), *args, **kwargs)
	return x


class DBDictServCursor(cursors.SSDictCursor):
	reconnect_timeout = 1
	reconnect_count = 0

	def __init__(self, conn):
		super(self.__class__, self).__init__(conn)

		for n in ['fetchall','fetchmany','fetchone','scroll','execute','executemany','nextset']:
			self.__dict__[n] = _runtime_decorator(self, n)


	def _call_parent(self, func, *args, **kwargs):
		err = None
		i = self.reconnect_count

		while True:
			try:
				return func(*args, **kwargs)
			except (AttributeError, MySQLdb.OperationalError), e:
				err = e

			if i == 0:
				break
			i -= 1

			if self.reconnect_timeout > 0:
				time.sleep(self.reconnect_timeout)

		raise DBError("Unable to connect to database: {0}", err)


class DBPool(object):

	_CONNECTIONS = {}

	def __init__(self, reconnect=0, timeout=1):
		self.reconnect = reconnect
		self.timeout   = timeout


	def get_item(self, dbhost=None, dbname=None, dbuser=None, dbpass=None, primarykey=None):
		"""Returns free connection"""

		conf = config.read()

		dbuser = dbuser or conf['database']['user']
		dbpass = dbpass or conf['database']['pass']
		dbname = dbname or conf['database']['name']
		dbhost = dbhost or get_host(primarykey)

		if not dbhost:
			raise DBError("Database host name is not specified")

		key = "{0}@{1}/{2}".format(dbuser,dbhost, dbname)

		if key not in self._CONNECTIONS:
			self._CONNECTIONS[key] = {}

		while True:
			for ids,sock in self._CONNECTIONS[key].iteritems():
				if sock['status'] == 'free':
					sock['status'] = 'busy'
					self.collect(key)
					return self._CONNECTIONS[key][ids]

			ids = str(uuid.uuid4())

			self._CONNECTIONS[key][ids] = {
				'key':    key,
				'ids':    ids,
				'status': 'free',
				'socket': MySQLdb.connect(
						cursorclass = DBDictServCursor,
						init_command= "SET autocommit=0",
						host        = dbhost,
						db          = dbname,
						user        = dbuser,
						passwd      = dbpass)
			}


	def collect(self, key=None):
		keys = [ key ]
		if not key:
			keys = self._CONNECTIONS.keys()

		for key in keys:
			garbage = []

			for ids,sock in self._CONNECTIONS[key].iteritems():
				if sock['status'] == 'free':
					garbage.append(sock)

			if not garbage:
				continue

			garbage.pop()

			for sock in garbage:
				self.close_connection(sock)


	def close_connection(self, conn):
		if conn['status'] != 'free':
			return
		del self._CONNECTIONS[conn['key']][conn['ids']]


	def free_connection(self, conn):
		conn['status'] = 'free'
		self.collect()

	def get_connection(self, dbname=None, primarykey=None):
		pitem = self.get_item(dbname, primarykey)
		return pitem['socket']


	def debug(self):
		return self._CONNECTIONS


class DBQuery(object):
	cursor = None

	def __init__(self, cursor, fmt, *args):
		self.cursor = cursor
		cursor.execute(fmt, *args)

	def __iter__(self):
		for o in self.cursor:
			yield o

	def one(self):
		if self.cursor:
			return self.cursor.fetchone()
		return None

	def all(self):
		if self.cursor:
			return self.cursor.fetchall()
		return None

	def __del__(self):
		self.cursor.close()


DB = DBPool()

class DBConnect(object):
	def __init__(self, dbhost=None, dbname=None, dbuser=None, dbpass=None, primarykey=None, commit=True):
		self.conn = DB.get_item(dbhost, dbname, dbuser, dbpass, primarykey)
		self.autocommit = commit


	def connect(self):
		return self.conn['socket']


	def __enter__(self):
		return self


	def __exit__(self, exc_type, exc_value, traceback):
		DB.free_connection(self.conn)
		return False


	def sql_where(self, query, sort=False):

		def sql_bool(x):
			if x == None:
				return 'NULL'
			return str(bool(x))

		def sql_optimize_operation(op, value):
			if op == '$eq':
				if isinstance(value, bool) or value == None:
					return '$is'
				if isinstance(value, list):
					return '$in'
			if op == '$ne':
				if isinstance(value, bool) or value == None:
					return '$notis'
				if isinstance(value, list):
					return '$nin'
			return op

		def sql_quote(op, value):
			if op in ['$is','$notis']:
				return sql_bool(value)

			if op in ['$in','$nin']:
				return ",".join(map(self.literal, value))

			if isinstance(value, dict) and op in ['$gt','$ge','$lt','$le','$eq','$ne']:
				if '$field' not in value:
					raise ValueError('Unsupported value type')
				return value['$field']

			return self.literal(value)

		concatenation = {
			'$and':    lambda x: " AND ".join(x),
			'$or':     lambda x:  " OR ".join(x),
		}
		operation = {
			'$gt':     lambda x,y: x + " > "          + y,
			'$ge':     lambda x,y: x + " >= "         + y,
			'$lt':     lambda x,y: x + " < "          + y,
			'$le':     lambda x,y: x + " <= "         + y,
			'$eq':     lambda x,y: x + " = "          + y,
			'$ne':     lambda x,y: x + " != "         + y,
			'$is':     lambda x,y: x + " IS "         + y,
			'$notis':  lambda x,y: x + " IS NOT "     + y,
			'$regex':  lambda x,y: x + " REGEXP "     + y,
			'$nregex': lambda x,y: x + " NOT REGEXP " + y,
			'$like':   lambda x,y: x + " LIKE "       + y,
			'$nlike':  lambda x,y: x + " NOT LIKE "   + y,
			'$in':     lambda x,y: x + " IN ("        + y + ")",
			'$nin':    lambda x,y: x + " NOT IN ("    + y + ")",
		}
		result = []
		for name, conditions in query.iteritems():
			if name == '$not':
				s = " NOT (" + self.sql_where(conditions, sort) + ")"
			elif name in concatenation:
				s = concatenation[name](map(
					lambda x: "(" + self.sql_where(x, sort) + ")",
					conditions))
			elif isinstance(conditions, dict):
				a = []
				for o, value in conditions.iteritems():
					o = sql_optimize_operation(o, value)
					v = sql_quote(o,value)
					r = operation[o](name,v)
					a.append(r)
				if sort:
					a.sort()
				s = concatenation['$and'](a)
			else:
				o = sql_optimize_operation('$eq', conditions)
				v = sql_quote(o, conditions)
				s = operation[o](name, v)

			result.append(s)

		if sort:
			result.sort()

		return concatenation['$and'](result)


	def commit(self):
		self.connect().commit()


	def rollback(self):
		self.connect().rollback()


	def escape(self, string):
		return self.connect().escape_string(str(string))


	def literal(self, string):
		return "'{0}'".format(self.escape(string))


	def exeute(self, fmt, *args):
		self.connect().cursor().execute(fmt, *args)
		if self.autocommit:
			self.commit()


	def delete(self, table, where=None):
		cond = ""
		if where:
			cond = "WHERE " + self.sql_where(where)
		self.connect().cursor().execute("DELETE FROM {0} {1};".format(table,cond))
		if self.autocommit:
			self.commit()


	def insert(self, table, dictionary):
		query = "INSERT INTO {0} ({1}) VALUES ({2});".format(table,
				",".join(dictionary.keys()),
				",".join(map(self.literal, dictionary.values())))
		self.connect().cursor().execute(query)
		if self.autocommit:
			self.commit()


	def update(self, table, search_dict, set_dict):
		new  = ", ".join(map(lambda x: "{0}={1}".format(x[0], self.literal(x[1])), set_dict.iteritems()))
		cond = self.sql_where(search_dict)
		self.connect().cursor().execute("UPDATE {0} SET {1} WHERE {2};".format(table, new, cond))
		if self.autocommit:
			self.commit()


	def query(self, fmt, *args):
		return DBQuery(self.connect().cursor(), fmt, *args)


	def find(self, tables, spec=None, fields=None, skip=0, limit=0):
		def delim(arr, delim=', '):
			n = len(arr) - 1
			for i in xrange(0, n):
				yield arr[i]
				yield delim
			yield arr[n]

		def genlist(arg, default):
			if isinstance(arg, list) and arg:
				return delim(arg)
			elif isinstance(arg, dict) and arg:
				return delim(map(lambda x: x[0]+' as '+x[1], arg.iteritems()))
			else:
				return [ default ]

		fmt = []
		fmt.append(" SELECT ")
		fmt.extend(genlist(fields, '*'))

		fmt.append(" FROM ")
		fmt.extend(genlist(tables, tables))

		if isinstance(spec, dict):
			fmt.extend([ " WHERE ", self.sql_where(spec) ])
		if limit > 0:
			fmt.extend([ " LIMIT ", str(limit) ])
		if skip > 0:
			fmt.extend([ " OFFSET ", str(skip) ])

		return self.query("".join(fmt))



	def find_one(self, *args, **kwargs):
		return self.find(*args, **kwargs).one()


def create_schema(dbname=None, dbuser=None, dbpass=None):
	with DBConnect(dbname=dbname, dbuser=dbuser, dbpass=dbpass) as db:
		for name, query in SCHEMA.iteritems():
			db.connect().cursor().execute(query.format(name))


def destroy_schema(dbname=None, dbuser=None, dbpass=None):
	with DBConnect(dbname=dbname, dbuser=dbuser, dbpass=dbpass) as db:
		for name in SCHEMA.keys():
			db.connect().cursor().execute("DROP TABLE IF EXISTS {0}".format(name))


SCHEMA = {
	'metrics': """
			CREATE TABLE `{0}` (
			  `id` varchar(128) NOT NULL,
			  `type` varchar(32) NOT NULL,
			  `formula` varchar(32) NOT NULL,
			  `aggregate` tinyint(1) NOT NULL,
			  PRIMARY KEY (`id`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
		""",

	'queue': """
			CREATE TABLE `{0}` (
			  `id` varchar(36) NOT NULL,
			  `customer` varchar(36) NOT NULL,
			  `rid` varchar(36) NOT NULL,
			  `state` enum('DONE','PROCESSING','AGGREGATE') NOT NULL,
			  `value` bigint(8) NOT NULL DEFAULT '1',
			  `time_check` int(11) NOT NULL,
			  `time_create` int(11) NOT NULL,
			  `time_destroy` int(11) NOT NULL DEFAULT '0',
			  `target_user` varchar(36) DEFAULT '',
			  `target_uuid` varchar(36) DEFAULT '',
			  `target_description` varchar(36) DEFAULT '',
			  PRIMARY KEY (`id`),
			  UNIQUE KEY `id_UNIQUE` (`id`),
			  KEY `search_INDEX` USING BTREE (`state`,`time_check`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
		""",
	'rates': """
			CREATE TABLE `{0}` (
			  `id` varchar(36) NOT NULL,
			  `description` varchar(1024) NOT NULL,
			  `mtype` varchar(36) NOT NULL,
			  `tariff_id` varchar(36) NOT NULL,
			  `rate` bigint(20) NOT NULL,
			  `currency` enum('RUR','USD','EUR') NOT NULL,
			  `state` enum('ACTIVE','ARCHIVE','UPDATING') NOT NULL,
			  `time_create` int(11) NOT NULL,
			  `time_destroy` int(11) NOT NULL,
			  `arg` varchar(36) DEFAULT '',
			  PRIMARY KEY (`id`),
			  UNIQUE KEY `id_UNIQUE` (`id`),
			  UNIQUE KEY `main_UNIQUE` USING BTREE (`state`,`mtype`,`tariff_id`,`arg`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
		""",
	'tariffs': """
			CREATE TABLE `{0}` (
			  `tariff_id` varchar(36) NOT NULL,
			  `name` varchar(45) NOT NULL,
			  `description` varchar(1024) NOT NULL,
			  `currency` enum('RUR','USD','EUR') NOT NULL,
			  `create_time` int(11) NOT NULL,
			  `state` enum('ENABLE','DISABLE') NOT NULL,
			  PRIMARY KEY (`tariff_id`),
			  UNIQUE KEY `tariff_id_UNIQUE` (`tariff_id`),
			  UNIQUE KEY `main_UNIQUE` USING BTREE (`state`,`tariff_id`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
		""",
	'customers': """
			CREATE TABLE `{0}` (
			  `id` varchar(36) NOT NULL,
			  `login` varchar(64) NOT NULL,
			  `name_short` varchar(255)  NOT NULL,
			  `name_full` varchar(1024) NOT NULL DEFAULT '',
			  `comment` varchar(1024) NOT NULL DEFAULT '',
			  `contract_client` varchar(255) NOT NULL DEFAULT '',
			  `contract_service` varchar(255) NOT NULL DEFAULT '',
			  `tariff_id` varchar(36) NOT NULL DEFAULT '',
			  `contact_person` varchar(255) NOT NULL DEFAULT '',
			  `contact_email` varchar(255) NOT NULL DEFAULT '',
			  `contact_phone` varchar(30) NOT NULL DEFAULT '',
			  `state` int NOT NULL DEFAULT '0',
			  `time_create` int(11) NOT NULL,
			  `time_destroy` int(11) NOT NULL DEFAULT '0',
			  `wallet` bigint NOT NULL DEFAULT '0',
			  `wallet_mode` int NOT NULL DEFAULT '0',
			  PRIMARY KEY (`id`),
			  UNIQUE KEY `id_UNIQUE` (`id`),
			  UNIQUE KEY `main_UNIQUE` (`login`, `state`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
	""",
	'auth_roles': """
			CREATE TABLE `{0}` (
			  `role` varchar(64) NOT NULL,
			  `method` varchar(64) NOT NULL,
			  `secret` varchar(1024) NOT NULL,
			  UNIQUE KEY `main_UNIQUE` USING BTREE (`role`, `method`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
	""",
}

