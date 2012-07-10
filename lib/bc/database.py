import os
import re
import time
import uuid
import logging

from bc import config
from bc import hashing

import psycopg2
from psycopg2 import extras

MIN_OPEN_CONNECTIONS = 1

# Backend exceptions:
OperationalError = psycopg2.OperationalError

# Backend methods
DBBackend_Cursor  = extras.RealDictCursor

def DBBackend_Connect(*args, **kwargs):
	return psycopg2.connect(
		host         = kwargs['dbhost'],
		database     = kwargs['dbname'],
		user         = kwargs['dbuser'],
		password     = kwargs['dbpass'],
	)


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


def sqldbg(qs):
	if os.environ.get('BILLING_SQL_DESCRIBE', False):
		LOG.debug("SQL: " + qs)


def _runtime_decorator(obj, n):
	def x(*args, **kwargs):
		return obj._call_parent(getattr(super(obj.__class__, obj), n), *args, **kwargs)
	return x


class DBCursor(DBBackend_Cursor):

	def __init__(self, conn):
		super(self.__class__, self).__init__(conn)

		self.reconnect_timeout = 1
		self.reconnect_count = 0

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

	def __init__(self, reconnect=0, timeout=1):
		self._CONNECTIONS = {}
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
						dbhost = dbhost,
						dbname = dbname,
						dbuser = dbuser,
						dbpass = dbpass)
			}


	def collect(self, k=None):
		keys = [ k ]
		if k == None:
			keys = self._CONNECTIONS.keys()

		for key in keys:
			garbage = []

			for ids,sock in self._CONNECTIONS[key].iteritems():
				if sock['status'] == 'free':
					garbage.append(sock)

			if len(garbage) <= MIN_OPEN_CONNECTIONS:
				continue

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

	def __init__(self, cursor, autocommit, fmt, *args):
		self.cursor = cursor
		self.autocommit = autocommit
		if self.autocommit:
			cursor.execute("START TRANSACTION")
		cursor.execute(fmt, *args)

	def close(self):
		self.cursor.fetchall()
		if self.autocommit:
			self.cursor.execute("COMMIT")
		self.cursor.close()

	def __iter__(self):
		for o in self.cursor:
			yield o
		self.close()

	def one(self):
		r = self.cursor.fetchone()
		self.close()
		return r

	def all(self):
		r = self.cursor.fetchall()
		self.close()
		return r


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
			self._cursor.close()
			self._cursor = None
		DB.free_connection(self._conn)
		return False


	def connect(self):
		"""Returns database connection
		"""
		return self._conn['socket']


	def cursor(self):
		"""Returns database cursor
		"""
		if not self._cursor:
			self._cursor = DBCursor(self.connect())
		return self._cursor


	def begin(self):
		"""Begins a new transaction block
		"""
		if self._transaction:
			return
		self.cursor().execute("START TRANSACTION")
		self._transaction = True


	def commit(self):
		"""Commits the current transaction
		"""
		if not self._transaction:
			return
		self.cursor().execute("COMMIT")
		self._transaction = False


	def savepoint(self, point, release=False):
		"""Establishes (or removes) a savepoint within the current transaction

		A savepoint is a special mark inside a transaction that allows all commands
		that are executed after it was established to be rolled back, restoring
		the transaction state to what it was at the time of the savepoint.

		Parameters:

		point:     the name of the savepoint;
		release:   destroys a savepoint previously defined.
		"""
		if not self._transaction:
			return
		qs = (release) and "RELEASE SAVEPOINT %s" or "SAVEPOINT %s"
		self.cursor().execute(qs, point)


	def rollback(self, point=None):
		"""Rolls back whole (or part) transaction

		Function rolls back all commands that were executed after
		the savepoint was established if 'point' parameter given.

		Parameters:

		point:   the name of the savepoint.
		"""
		if not self._transaction:
			return
		if point != None:
			self.cursor().execute("ROLLBACK TO SAVEPOINT %s", point)
			return
		self.cursor().execute("ROLLBACK")
		self._transaction = False


	def execute(self, fmt, *args):
		"""Exetutes SQL command
		"""
		self.begin()
		self.cursor().execute(fmt, *args)
		if self._autocommit:
			self.commit()


	def query(self, fmt, *args):
		"""Queries the database and returns DBCursor with result
		"""
		cur = DBCursor(self.connect())
		return DBQuery(cur, self._autocommit, fmt, *args)


	def sql_update(self, query, sort=False):
		"""Converts mongo-like dictionary to SET condition for UPDATE statement
		"""
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
		"""Converts mongo-like dictionary to SQL WHERE statement
		"""
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
		"""Escapes any special characters
		"""
		if isinstance(string, (basestring, unicode)):
			return re.sub(r'([\'\"\\])', r'\\\1', str(string))
		return str(string)
		#return self.connect().escape_string(str(string))


	def literal(self, string):
		"""Returns SQL string literal

		If 'string' is a single object, returns an SQL literal as a string.
		If 'string' is a non-string sequence, the items of the sequence are
		converted and returned as a sequence.
		"""
		return "'{0}'".format(self.escape(string))


	def _delim(self, arr, delim=', '):
		n = len(arr) - 1
		for i in xrange(0, n):
			yield arr[i]
			yield delim
		yield arr[n]


	def _genlist(self, arg, default):
		if isinstance(arg, list) and arg:
			return self._delim(arg)
		elif isinstance(arg, dict) and arg:
			return self._delim(map(lambda x: x[0]+' as '+x[1], arg.iteritems()))
		else:
			return [ default ]


	def delete(self, table, spec=None, returning=None):
		"""Removes a document(s) from this table

		Parameters:

		table:     specify a table name;

		spec:      a dictionary specifying the documents to be removed;

		returning: The optional argument that causes delete() to compute and
		           return value(s) based on each row actually updated.
		           The syntax of the 'returning' list is identical to that
		           of the output list of find().
		"""

		fmt = [ " DELETE FROM ", table ]

		if isinstance(spec, dict) and len(spec) > 0:
			fmt.extend([ " WHERE ", self.sql_where(spec) ])

		need_return = isinstance(returning, (dict, list))

		if need_return:
			fmt.append(" RETURNING ")
			if len(returning) > 0:
				fmt.extend(self._genlist(returning, '*'))
			else:
				fmt.append('*')

		qs = "".join(fmt)
		sqldbg(qs)

		if need_return:
			return self.query(qs)
		self.execute(qs)


	def insert(self, table, document, returning=None):
		"""Inserts a document(s) into this table

		Parameters:

		table:     specify a table name;

		document:  a document to be inserted.

		returning: The optional argument that causes insert() to compute and
		           return value(s) based on each row actually updated.
		           The syntax of the 'returning' list is identical to that
		           of the output list of find().
		"""

		if not isinstance(document, (dict, list)):
			raise TypeError("Wrong type of 'document': {1}".format(type(document).__name__))

		if len(document) == 0:
			raise ValueError("The 'document' should not be empty")

		if isinstance(document, (dict)):
			document = [ document ]

		fmt = [ " INSERT INTO ", table ]

		keys = sorted(document[0].keys())
		fmt.extend([ "(", ",".join(keys), ")" ])

		vals = []
		for o in document:
			# This is a simple protection against errors.
			# We add value only by the keys from the first element.
			vals.append("(")
			vals.extend(self._delim(map(lambda x: self.literal(o[x]), keys)))
			vals.extend([ ")", "," ])
		vals.pop()
		fmt.extend([ " VALUES ", "".join(vals) ] )

		need_return = isinstance(returning, (dict, list))

		if need_return:
			fmt.append(" RETURNING ")
			if len(returning) > 0:
				fmt.extend(self._genlist(returning, '*'))
			else:
				fmt.append('*')

		qs = "".join(fmt)
		sqldbg(qs)

		if need_return:
			return self.query(qs)
		self.execute(qs)


	def update(self, tables, spec, document, returning=None):
		"""Updates a document(s) in this table(s)

		Parameters:

		tables:   specify a table name or list of names;

		spec:     a dict or SON instance specifying elements which
		          must be present for a document to be updated;

		document: a dict or SON instance specifying the document to be used
		          for the update;

		returning: The optional argument that causes update() to compute and
		           return value(s) based on each row actually updated.
		           The syntax of the 'returning' list is identical to that
		           of the output list of find().
		"""

		for n,o in [ ('document',document), ('spec',spec) ]:
			if not isinstance(o, dict):
				raise TypeError("Wrong type of '{0}': {1}".format(n, type(o).__name__))

		if len(document) == 0:
			raise ValueError("The 'document' should not be empty")

		fmt = [ " UPDATE " ]
		fmt.extend(self._genlist(tables, tables))
		fmt.extend([ " SET ", self.sql_update(document) ])

		if len(spec) > 0:
			fmt.extend([ " WHERE ", self.sql_where(spec) ])

		need_return = isinstance(returning, (dict, list))

		if need_return:
			fmt.append(" RETURNING ")
			if len(returning) > 0:
				fmt.extend(self._genlist(returning, '*'))
			else:
				fmt.append('*')

		qs = "".join(fmt)
		sqldbg(qs)

		if need_return:
			return self.query(qs)
		self.execute(qs)


	def find(self, tables, spec=None, fields=None, sort=None, skip=0, limit=0, lock=None, nowait=False):
		"""Query the database

		The spec argument is a prototype document that all results must match.
		Returns an instance of Cursor corresponding to this query.

		Parameters:

		spec:   a SON object specifying elements which must be present
		        for a document to be included in the result set;

		fields: a list of field names that should be returned
		        or a dict specifying the fields to return;

		skip:   the number of documents to omit (from the start of the result set)
		        when returning the results;

		limit:  the maximum number of results to return;

		sort:   a list of (key, direction) pairs specifying the sort order
		        for this query.
		"""

		fmt = []
		fmt.append(" SELECT ")
		fmt.extend(self._genlist(fields, '*'))

		fmt.append(" FROM ")
		fmt.extend(self._genlist(tables, tables))

		if isinstance(spec, dict):
			fmt.extend([ " WHERE ", self.sql_where(spec) ])

		if sort != None and len(sort) > 0:
			fmt.append(" ORDER BY")
			fmt.append(', '.join(map(lambda x: ' '.join(x), sort)))

		if limit > 0:
			fmt.extend([ " LIMIT ", str(limit) ])
		if skip > 0:
			fmt.extend([ " OFFSET ", str(skip) ])

		if lock != None:
			if lock == 'update':
				fmt.append(" FOR UPDATE")

			elif lock == 'share':
				# Another syntax in MySQL: LOCK IN SHARE MODE
				fmt.append(" FOR SHARE")

			# Unsupported in MySQL
			if nowait:
				fmt.append(" NOWAIT")

		qs = "".join(fmt)
		sqldbg(qs)

		return self.query(qs)


	def find_one(self, *args, **kwargs):
		"""Gets a single document from the database

		All arguments to find() are also valid arguments for find_one(),
		although any limit argument will be ignored. Returns a single document,
		or None if no matching document is found.
		"""
		return self.find(*args, **kwargs).one()

