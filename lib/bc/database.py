import os
import time
import uuid
import logging

from bc import config
from bc import hashing
from bc import log

from bc import database_schema

DATABASE_BACKEND = 'mysql'

if DATABASE_BACKEND == 'mysql':
	import MySQLdb
	from MySQLdb import cursors

	# Backend exceptions:
	OperationalError = MySQLdb.OperationalError
	ProgrammingError = MySQLdb.ProgrammingError

	# Backend methods
	DBBackend_Connect = MySQLdb.connect
	DBBackend_Cursor  = cursors.SSDictCursor


LOG = logging.getLogger("database")

class DBError(Exception):
	"""The base class for database exceptions that our code throws"""

	def __init__(self, error, *args):
		Exception.__init__(self, unicode(error).format(*args) if len(args) else unicode(str(error)))


def get_host(key=None):
	"""Returns database server"""

	conf = config.read()

	if len(conf['database']['shards']) > 0 and isinstance(key, basestring):
		ring = hashing.HashRing(conf['database']['shards'])
		host = ring.get_node(key)
	else:
		host = conf['database']['server']

	return host


def _runtime_decorator(obj, n):
	def x(*args, **kwargs):
		return obj._call_parent(getattr(super(obj.__class__, obj), n), *args, **kwargs)
	return x


class DBDictServCursor(DBBackend_Cursor):
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
			except (AttributeError, OperationalError), e:
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
				'socket': DBBackend_Connect(
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


DB = DBPool()

class DBConnect(object):
	_autocommit  = True
	_transaction = False
	_conn        = None
	_cursor      = None

	def __init__(self, dbhost=None, dbname=None, dbuser=None, dbpass=None, primarykey=None, commit=True):
		self._conn = DB.get_item(dbhost, dbname, dbuser, dbpass, primarykey)
		self._autocommit = commit
		self._transaction = False


	def __enter__(self):
		return self


	def __exit__(self, exc_type, exc_value, traceback):
		if self._cursor:
			self.commit()
			self._cursor = None
		DB.free_connection(self._conn)
		return False


	def connect(self):
		return self._conn['socket']


	def cursor(self):
		if not self._cursor:
			self._cursor = DBDictServCursor(self.connect())
		return self._cursor


	def begin(self):
		if self._transaction:
			return
		self.cursor().execute("START TRANSACTION")
		self._transaction = True

	def commit(self):
		if not self._transaction:
			return
		try:
			self.cursor().execute("COMMIT")
		except ProgrammingError:
			pass
		self._transaction = False


	def rollback(self):
		if not self._transaction:
			return
		try:
			self.cursor().execute("ROLLBACK")
		except ProgrammingError:
			pass
		self._transaction = False


	def execute(self, fmt, *args):
		self.begin()
		self.cursor().execute(fmt, *args)
		if self._autocommit:
			self.commit()


	def query(self, fmt, *args):
		self.begin()
		return DBQuery(self.cursor(), fmt, *args)


	def sql_update(self, query, sort=False):
		bit_ops = {
			'and':    lambda x: '&'  + arg(x),
			'or':     lambda x: '|'  + arg(x),
			'xor':    lambda x: '^'  + arg(x),
			'rshift': lambda x: '>>' + arg(x),
			'lshift': lambda x: '<<' + arg(x),
		}
		func_ops = {
			'$field': lambda x: (str(x),),
			'$abs':   lambda x: ('ABS('   + arg(x) + ')',),
			'$ceil':  lambda x: ('CEIL('  + arg(x) + ')',),
			'$crc32': lambda x: ('CRC32(' + arg(x) + ')',),
			'$floor': lambda x: ('FLOOR(' + arg(x) + ')',),
			'$mod':   lambda x: ('MOD('   + arg(x[0]) + ',' + arg(x[1]) + ')',),
			'$round': lambda x: (len(x) == 2 and 'ROUND(' + arg(x[0]) + ',' + arg(x[1]) + ')' or 'ROUND(' + arg(x[0]) + ')',),
		}
		ops = {
			'$bit':    lambda x:   bit_ops[x[0]](x[1]),
			'$set':    lambda x,y: x + "=" + arg(y),
			'$dec':    lambda x,y: x + "=" + x + "-" + arg(y),
			'$inc':    lambda x,y: x + "=" + x + "+" + arg(y),
			'$div':    lambda x,y: x + "=" + x + "/" + arg(y),
			'$mult':   lambda x,y: x + "=" + x + "*" + arg(y),
			'$concat': lambda x,y: x + "=CONCAT(" + x + "," +  self.literal(y) + ")",
		}

		def arg(x):
			if isinstance(x, basestring):
				return self.literal(x)
			if isinstance(x, tuple):
				return x[0]
			return str(x)

		def resole_op(arg):
			k,v = arg.popitem()
			if isinstance(v, dict):
				return func_ops[k](resole_op(v))
			return func_ops[k](v)

		res = []
		for op,cond in query.iteritems():
			if op in [ '$set', '$inc', '$dec', '$div', '$mult' ]:
				for n,v in cond.iteritems():
					if isinstance(v, dict):
						res.append(ops[op](n, resole_op(v)))
					else:
						res.append(ops[op](n, v))
			elif op == '$concat':
				res.extend(map(lambda x: ops[op](x[0],x[1]),cond.iteritems()))
			elif op == '$bit':
				res.extend(map(lambda x: x[0]+"="+x[0]+"".join(map(ops[op],x[1].iteritems())),cond.iteritems()))
			else:
				res.append(op + "=" + self.literal(cond))

		if sort:
			res.sort()

		return ", ".join(res)


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
				a = map(lambda x: "(" + self.sql_where(x, sort) + ")", conditions)
				s = "(" + concatenation[name](a) + ")"
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



	def escape(self, string):
		return self.connect().escape_string(str(string))


	def literal(self, string):
		return "'{0}'".format(self.escape(string))


	def delete(self, table, where=None):
		qs = "DELETE FROM {0} {1};".format(table,
			(where == None and "" or "WHERE " + self.sql_where(where)))

		if os.environ.get('BILLING_SQL_DESCRIBE', False):
			LOG.debug("SQL: " + qs)

		self.execute(qs)


	def insert(self, table, dictionary):
		qs = "INSERT INTO {0} ({1}) VALUES ({2});".format(table,
			",".join(dictionary.keys()),
			",".join(map(self.literal, dictionary.values())))

		if os.environ.get('BILLING_SQL_DESCRIBE', False):
			LOG.debug("SQL: " + qs)

		self.execute(qs)


	def update(self, table, search_dict, set_dict):
		qs = "UPDATE {0} SET {1} WHERE {2};".format(table,
			self.sql_update(set_dict),
			self.sql_where(search_dict))

		if os.environ.get('BILLING_SQL_DESCRIBE', False):
			LOG.debug("SQL: " + qs)

		self.execute(qs)


	def find(self, tables, spec=None, fields=None, skip=0, limit=0, lock=None):
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

		if lock == 'update':
			fmt.append(" FOR UPDATE")
		elif lock == 'shared':
			fmt.append(" LOCK IN SHARE MODE")

		qs = "".join(fmt)

		if os.environ.get('BILLING_SQL_DESCRIBE', False):
			LOG.debug("SQL: " + qs)

		return self.query(qs)


	def find_one(self, *args, **kwargs):
		return self.find(*args, **kwargs).one()


def create_schema(dbname=None, dbuser=None, dbpass=None):
	with DBConnect(dbname=dbname, dbuser=dbuser, dbpass=dbpass, commit=False) as db:
		for name, query in database_schema.SCHEMA.iteritems():
			db.execute(query.format(name))
		db.commit()


def destroy_schema(dbname=None, dbuser=None, dbpass=None):
	with DBConnect(dbname=dbname, dbuser=dbuser, dbpass=dbpass, commit=False) as db:
		for name in database_schema.SCHEMA.keys():
			db.execute("DROP TABLE IF EXISTS {0}".format(name))
		db.commit()

