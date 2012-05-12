import time
import MySQLdb
from MySQLdb import cursors

import config
import hashing


_CONNECTIONS = {}
"""Database connections."""


class DBError(Exception):
	"""The base class for database exceptions that our code throws"""

	def __init__(self, error, *args):
		Exception.__init__(self, unicode(error).format(*args) if len(args) else unicode(str(error)))


def get_host(key = None):
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


class DBDictCursor(cursors.DictCursor):
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
		raise err


class DB(object):
	conn = None
	name = None
	host = None

	def __init__(self, primarykey = None, dbname = None, reconnect = 0, timeout = 1, commit = True):
		conf = config.read()
		self.commit = commit
		self.name   = dbname or conf['database']['name']
		self.user   = conf['database']['user']
		self.passwd = conf['database']['pass']
		self.host   = get_host(primarykey)

		if not self.host:
			raise DBError("Database host name is not specified")

		self.reconnect  = reconnect
		self.timeout    = timeout

		self.connect()


	def connect(self):
		key = self.host + "/" + self.name

		if key not in _CONNECTIONS:
			_CONNECTIONS[key] = MySQLdb.connect(
				host        = self.host,
				db          = self.name,
				user        = self.user,
				passwd      = self.passwd,
				cursorclass = DBDictCursor
			)

		self.conn = _CONNECTIONS[key]
		return self


	def disconnect(self):
		self.conn.close()
		return self


	def ping(self):
		self.conn.ping()
		return self


	def autocommit(self, mode):
		self.conn.autocommit(bool(mode))
		return self


	def cursor(self, cls=None):
		err = None
		i = self.reconnect

		while True:
			try:
				return self.conn.cursor(cls)

			except (AttributeError, MySQLdb.OperationalError), e:
				err = e

			if i == 0:
				break
			i -= 1

			if self.timeout > 0:
				time.sleep(self.timeout)

			self.connect()

		raise DBError("Unable to connect to database: {0}", err)


	def escape(self, string):
		return self.conn.escape_string(str(string))


	def insertdict(self, table, dictionary):
		join = lambda x, y: "{0}, {0}".format(y).join(map(self.escape, x)).join([y,y])
		queue = "INSERT INTO {0} ({1}) VALUES ({2});".format(table,
				join(dictionary.keys(),'`'),
				join(dictionary.values(),"'"))
		self.cursor().execute(queue)
		if self.commit:
			self.conn.commit()


	def query(self, fmt, *args):
		cur = self.cursor()
		res = cur.execute(fmt, *args)
		if res == 0:
			raise StopIteration
		for o in cur:
			yield o


	def create_queue(self, name):
		self.cursor().execute(SCHEMA['queue_skeleton'].format(name))


	def create_schema(self):
		for name, query in SCHEMA.iteritems():
			if name in DYNAMIC_TABLES:
				continue
			self.cursor().execute(query.format(name))



DYNAMIC_TABLES = ['queue_skeleton']
SCHEMA = {
	'metrics': """
			CREATE TABLE `{0}` (
			  `mtype` varchar(36) NOT NULL,
			  `time_type` int(11) NOT NULL,
			  `aggregate` tinyint(1) NOT NULL,
			  `time_dimention_koef` int(11) NOT NULL,
			  `count_dimention_koef` int(11) NOT NULL,
			  `count_dimention_type` varchar(45) NOT NULL,
			  PRIMARY KEY (`mtype`)
			) DEFAULT CHARSET=utf8;
		""",

	'queue_skeleton': """
			CREATE TABLE `{0}` (
			  `uuid` varchar(36) NOT NULL,
			  `customer` varchar(36) NOT NULL,
			  `rid` varchar(36) NOT NULL,
			  `rate` bigint(20) NOT NULL,
			  `description` varchar(1024) NOT NULL,
			  `state` enum('DONE','PROCESSING','AGGREGATE') NOT NULL,
			  `value` bigint(20) NOT NULL DEFAULT '1',
			  `time_now` int(11) NOT NULL,
			  `time_check` int(11) NOT NULL,
			  `time_create` int(11) NOT NULL,
			  `time_destroy` int(11) NOT NULL,
			  `target_user` varchar(36) DEFAULT NULL,
			  `target_uuid` varchar(36) DEFAULT NULL,
			  `target_description` varchar(36) DEFAULT NULL,
			  PRIMARY KEY (`uuid`),
			  UNIQUE KEY `uuid_UNIQUE` (`uuid`)
			) DEFAULT CHARSET=utf8;
		""",
	'rates': """
			CREATE TABLE `{0}` (
			  `rid` varchar(36) NOT NULL,
			  `description` varchar(1024) NOT NULL,
			  `mtype` varchar(36) NOT NULL,
			  `tariff_id` varchar(36) NOT NULL,
			  `rate_value` bigint(20) NOT NULL,
			  `rate_currency` enum('RUR','USD','EUR') NOT NULL,
			  `state` enum('ACTIVE','ARCHIVE','UPDATING') NOT NULL,
			  `time_create` int(11) NOT NULL,
			  `time_destroy` int(11) NOT NULL,
			  `arg` varchar(36) DEFAULT NULL,
			  PRIMARY KEY (`rid`),
			  UNIQUE KEY `rid_UNIQUE` (`rid`)
			) DEFAULT CHARSET=utf8;
		""",
	'tariffs': """
			CREATE TABLE `{0}` (
			  `tariff_id` varchar(36) NOT NULL,
			  `name` varchar(45) NOT NULL,
			  `description` varchar(1024) NOT NULL,
			  `currency` enum('RUR','USD','EUR') NOT NULL,
			  `create_time` int(11) NOT NULL,
			  `state` enum('ARCHIVE','ACTIVE') NOT NULL,
			  PRIMARY KEY (`tariff_id`)
			) DEFAULT CHARSET=utf8;
		""",
}
