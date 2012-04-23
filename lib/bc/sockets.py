#!/usr/bin/env python2.6

import os, socket, threading, time, struct, errno, logging
import msgpack
#import traceback

def recv_failure_retry(sock, rlen):
	"""Recv socket and repeat as long as it returns with `errno'
	   set to EINTR."""

	res = ""
	bytes = rlen
	while bytes > 0:
		try:
			buf = sock.recv(bytes)
			if not buf: break

			bytes -= len(buf)
			res   += buf

		except socket.error, e:
			if e.errno != errno.EINTR:
				raise e
	return res


def send_data(sock, obj):
	data_str = msgpack.packb(obj)
	data_len = len(data_str)

	msg = struct.pack('Q', data_len)
	msg += data_str

	sock.sendall(msg)


class Socket(object):
	def __init__(self, sock):
		self.sock = sock
		self.rd_lock = threading.Lock()
		self.wr_lock = threading.Lock()


	def recv(self, bytes):
		res = ""
		try:
			self.rd_lock.acquire()
			res = recv_failure_retry(self.sock, bytes)
		finally:
			self.rd_lock.release()
		return res


	def send(self, data):
		try:
			self.wr_lock.acquire()
			send_data(self.sock, data)
		finally:
			self.wr_lock.release()

	def close(self):
		try:
			self.sock.shutdown(socket.SHUT_RDWR)
			self.sock.close()
		except:
			pass # Ignore any errors


class Server(object):
	def __init__(self, host='localhost', port=9999):
		    self.handlers = {
			    'on_connect':    None,
			    'on_disconnect': None,
			    'on_recv':       None,
			    'on_err':        self.default_err_handler
		    }
		    self.host  = host
		    self.port  = port
		    self.sock  = None


	def default_err_handler(self, e):
		#traceback.print_exc()
		logging.error(e)


	def recv(self, conn):
		# Calculate pack size
		n = struct.calcsize('Q')

		try:
			# Get message length
			m = conn.recv(n)
			if not m:
				return None

			mlen = struct.unpack('Q', m)
			mlen = int(mlen[0])

			# Read payload
			data = conn.recv(mlen)

			# Return valid python object
			return msgpack.unpackb(data)

		except Exception, e:
			self.handle('on_err', e)

		return None


	def accept_connection(self, conn, addr):
	    try:
		    self.handle('on_connect', addr, conn)

		    while True:
			    data = self.recv(conn)
			    if not data: break
			    self.handle('on_recv', addr, conn, data)

		    self.handle('on_disconnect', addr, conn)
		    conn.close()

	    except Exception, e:
		    self.handle('on_err', e)


	def bind(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
		self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

		self.sock.bind((self.host, self.port))


	def run(self):
		try:
			# will fail when port as busy, or we don't have rights to bind
			self.bind()
			self.sock.listen(socket.SOMAXCONN)

			while True:
				sock, addr = self.sock.accept()
				conn = Socket(sock)

				c = threading.Thread(target=self.accept_connection, args=[conn, addr, ])
				c.setDaemon(True)
				c.start()

		except socket.error, e:
			self.handle('on_err', e)


	def start(self, timeout=0):
		t = threading.Thread(target=self.run)
		t.daemon = True
		t.start()
		time.sleep(timeout)
		return t


	def set_handlers(self, handlers):
		if not isinstance(handlers, dict):
			return False

		for name in self.handlers.keys():
			if name in handlers:
				self.handlers[name] = handlers[name]
		return True


	def handle(self, name, *args, **kwargs):
		try:
			if name in self.handlers and self.handlers[name] != None:
				self.handlers[name](*args, **kwargs)

		except Exception, e:
			self.handle('on_err', e)


class Client(object):
	def __init__(self, host='localhost', port=9999):
		    self.handlers = {
			    'on_connect':    None,
			    'on_disconnect': None,
			    'on_recv':       None,
			    'on_err':        self.default_err_handler
		    }
		    self.host = host
		    self.port = port
		    self.sock = None


	def default_err_handler(self, e):
		#traceback.print_exc()
		logging.error(e)


	def connect(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((self.host, self.port))
		self.sock = Socket(sock)


	def close(self):
		#addr = (self.host, self.port)
		#self.handle('on_disconnect', addr, self.sock)
		self.sock.close()


	def recv(self):
		# Calculate pack size
		n = struct.calcsize('Q')

		try:
			# Get message length
			m = self.sock.recv(n)
			if not m:
				return None

			mlen = struct.unpack('Q', m)
			mlen = int(mlen[0])

			# Read payload
			data = self.sock.recv(mlen)

			# Return valid paython object
			return msgpack.unpackb(data)

		except Exception, e:
			self.handle('on_err', e)

		return None


	def send(self, data):
		try:
			self.sock.send(data)

		except Exception, e:
			self.handle('on_err', e)


	def run(self):
		addr = (self.host, self.port)
		try:
			self.connect()
			self.handle('on_connect', addr, self.sock)

			while True:
				data = self.recv()
				if not data: break
				self.handle('on_recv', addr, self.sock, data)

			self.handle('on_disconnect', addr, self.sock)
			self.close()

		except socket.error, e:
			self.handle('on_err', e)


	def start(self, timeout=0):
		t = threading.Thread(target=self.run)
		t.daemon = True
		t.start()
		time.sleep(timeout)
		return t


	def set_handlers(self, handlers):
		if not isinstance(handlers, dict):
			return False

		for name in self.handlers.keys():
			if name in handlers:
				self.handlers[name] = handlers[name]
		return True


	def handle(self, name, *args, **kwargs):
		try:
			if name in self.handlers and self.handlers[name] != None:
				self.handlers[name](*args, **kwargs)

		except Exception, e:
			self.handle('on_err', e)

