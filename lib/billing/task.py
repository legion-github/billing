#!/usr/bin/python

__version__ = '1.0'

__all__ = [
	'Task', 'BillingTask',
	'UUID', 'NAME', 'CUSTOMER', 'USER', 'DATA',
]
import httplib
import random
import json
import uuid
import time

from c2 import config
from c2 import constants
from c2 import mongodb
from c2.core import InternalError

from bc.jsonrpc.http import jsonrpc_http_request


NAME         = 'type'
CUSTOMER     = 'customer'
USER         = 'user'
DATA         = 'info'
TIME_CREATE  = 'time-create'
TIME_DESTROY = 'time-destroy'

class Task(object):
	def __init__(self, o = None):
		self.__values = {
			UID:		str(uuid.uuid4()),
			NAME:		'',
			USER:		'',
		#	CUSTOMER:	'',
			TIME_CREATE:	int(time.time()),
			TIME_DESTROY:	0,
			DATA:		{},
		}
		if o:
			self.set(o)


	def __repr__(self):
		return repr(self.__values)


	def __str__(self):
		return str(self.__values)


	def to_json(self):
		return json.dumps(self.__values)


	def from_json(self, o):
		self.set(json.loads(o))
		return self


	def set(self, o):
		for name in self.__values:
			if name in o:
				self.__setitem__(name, o.get(name))
		return self


	def get(self):
		return dict(self.__values)


	def __setitem__(self, name, value):
		if name in self.__values:
			typ = type(self.__values.get(name))

			if not isinstance(value, typ):
				raise TypeError

			if typ in [ int, long ] and value < 0:
				raise ValueError("Value must be greater than 0")

			self.__values[name] = value
		else:
			raise KeyError


	def __getitem__(self, name):
		if name in self.__values:
			return self.__values.get(name)
		raise KeyError


	def __delitem__(self, name):
		if name in self.__values:
			self.__values[name] =  type(self.__values.get(name))()


class BillingTask(Task):
	__conn  = None
	__host  = None

	def __connect(self):
		if self.__conn:
			return

		hosts = config.BILLING_HOSTS.split(",")
		random.shuffle(hosts)

		for host in hosts:
			try:
				self.__conn = httplib.HTTPConnection(host, timeout = config.CONNECT_TIMEOUT)
				self.__conn.connect()
				self.__conn.timeout = config.NETWORK_TIMEOUT
				self.__conn.sock.settimeout(self.__conn.timeout)
				self.__host = host

			except Exception as e:
				LOG.error("Failed to connect to %s: %s.", host, e)
			else:
				break
		else:
			raise InternalError()


	def __send(self, method, auth):
		try:
			autho = None

			if auth:
				autho = {
					'role':   config.BILLING_ROLE,
					'secret': config.BILLING_SECRET
				}

			res = jsonrpc_http_request(self.__conn, method, self.get(),
				auth_data = autho,
				req_limit = constants.MEGABYTE)

		except Exception as e:
			LOG.error("Failed to communicate with '%s': %s", self.__host, e)
			raise InternalError()

		finally:
			self.__conn.close()
			self.__conn = None

		if 'result' in res:
			return res['result']

		if 'error' in res:
			return res['error']

		return None


	def test(self, auth = True):
		self.__connect()
		return self.__send('Test', auth)


	def open(self, auth = True):
		self.__connect()
		return self.__send('taskOpen', auth)


	def reopen(self, auth = True):
		self.__connect()
		return self.__send('taskReopen', auth)


	def close(self, auth = True):
		self.__connect()
		return self.__send('taskClose', auth)
