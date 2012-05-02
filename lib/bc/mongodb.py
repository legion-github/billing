#!/usr/bin/env python

import atexit
import time
import pymongo

from bc import config
from bc import hashing


_CONNECTIONS = {}
"""MongoDB connections."""


class DBError(Exception):
	"""The base class for database exceptions that our code throws"""

	def __init__(self, error, *args):
		Exception.__init__(self, unicode(error).format(*args) if len(args) else unicode(str(error)))


class CallProxy(object):
	def __init__(self, func, reconnect = 0, timeout = 1):
		self.__reconnect = reconnect
		self.__timeout = timeout
		self.__func = func

	def __call__(self, *args, **kwargs):
		err = None
		i = self.__reconnect
		while True:
			try:
				return self.__func(*args, **kwargs)
			except pymongo.errors.ConnectionFailure, e: err = e
			except pymongo.errors.AutoReconnect, e:     err = e

			if i <= 1: break
			time.sleep(self.__timeout)
			i -= 1
		raise err


class collection(object):
	"""Collection from the billing database."""

	def __init__(self, name, primarykey = None, reconnect = 0, timeout = 1):
		conf = config.read()

		database = conf['database']['name']
		host = get_host(primarykey)

		self.reconnect  = reconnect
		self.timeout    = timeout
		self.connection = connection(host)
		self.collection = self.connection[database][name]

		if not host:
			raise DBError("Database host name is not specified")


	def __getattr__(self, name):
		value = getattr(self.collection, name)
		if callable(value):
			return CallProxy(value, self.reconnect, self.timeout)
		else:
			return value


	def __getitem__(self, name):
		return self.collection[name]


	def __repr__(self):
		return "CollectionDB(%r, %r, reconnect=%r, timeout=%r)" % (
		    self.collection.database, self.collection.name,
		    self.reconnect, self.timeout)


def close():
	"""Closes all opened connections.
	
	It may be useful because pymongo has a bug due to which broken connections
	remain broken regardless of the auto reconnect feature.
	"""

	_CONNECTIONS.clear()


def get_host(key = None):

	conf = config.read()

	if isinstance(key, basestring):
		ring = hashing.HashRing(conf['database']['shards'])
		host = ring.get_node(key)
	else:
		host = conf['database']['server']

	return host


def connection(host):
	global _CONNECTIONS
	connection = _CONNECTIONS.get(host)

	if connection is None:
		try:
			connection = pymongo.Connection(host, network_timeout = 30)
			_CONNECTIONS[host] = connection

		except Exception, e:
			raise DBError("Unable to connect to MongoDB: {0}", e)
	return connection


atexit.register(close)

