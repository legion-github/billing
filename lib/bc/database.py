import time
import MySQLdb
from MySQLdb import cursors

import config


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


class DB:
	conn = None
	name = None
	host = None

	def __init__(self, primarykey = None, reconnect = 0, timeout = 1):
		conf = config.read()

		self.name = conf['database']['name']
		self.host = get_host(primarykey)

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
				cursorclass = DBDictCursor
			)

		self.conn = _CONNECTIONS[key]
		return self


	def disconnect(self):
		self.conn.close()
		return self


	def cursor(self):
		err = None
		i = self.reconnect

		while True:
			try:
				return self.conn.cursor()

			except (AttributeError, MySQLdb.OperationalError), e:
				err = e

			if i == 0:
				break
			i -= 1

			if self.timeout > 0:
				time.sleep(self.timeout)

			self.connect()

		raise DBError("Unable to connect to database: {0}", err)


	def __getattr__(self, name):
		value = getattr(self.collection, name)
		if callable(value):
			return CallProxy(value, self.reconnect, self.timeout)
		else:
			return value


	def __getitem__(self, name):
		return self.collection[name]


#cur = DB().cursor()
#res = cur.execute("show variables")
#for o in cur.fetchall():
#	print o
#cur = DB().cursor()
#res = cur.execute("show variables")
