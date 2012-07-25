#!/usr/bin/env python2.6

import socket as pysocket
import threading, time, struct, errno, logging
import msgpack


class Socket(object):
	def __init__(self, socket=None, family=socket.AF_INET, typ=socket.SOCK_STREAM, proto=0):
		self.sock = socket or pysocket.socket(family, typ, proto)

		for n in [ 'setsockopt', 'accept', 'bind', 'connect' ]:
			self.__dict__[n] = getattr(self.sock, n)

		self.rd_lock = threading.Lock()
		self.wr_lock = threading.Lock()


	def __recv_failure_retry(self, rlen):
		"""Recv socket and repeat as long as it returns with `errno' set to EINTR."""
		res = []
		bytes = int(rlen)
		while bytes > 0:
			try:
				buf = self.sock.recv(bytes)
				if not buf: break

				bytes -= len(buf)
				res.append(buf)

			except pysocket.error, e:
				if e.errno != errno.EINTR:
					raise e
		return ''.join(res)


	def recv(self, bytes):
		try:
			self.rd_lock.acquire()
			return self.__recv_failure_retry(bytes)
		finally:
			self.rd_lock.release()
		return ""


	def send(self, data):
		try:
			self.wr_lock.acquire()
			data_str = msgpack.packb(data)
			self.sock.sendall(struct.pack('Q', len(data_str)) + data_str)
		finally:
			self.wr_lock.release()


	def close(self):
		try:
			self.sock.shutdown(pysocket.SHUT_RDWR)
			self.sock.close()
		except:
			pass # Ignore any errors


class ServerBase(object):
	def recv(self, sock):
		try:
			# Calculate pack size
			n = struct.calcsize('Q')

			# Get message length
			m = sock.recv(n)
			if not m:
				return None

			# Calculate payload size
			mlen = int(struct.unpack('Q', m)[0])

			# Read payload
			data = sock.recv(mlen)

			# Return valid python object
			return msgpack.unpackb(data)

		except Exception, e:
			self.on_error(e)
		return None

	def on_connect(self, addr, sock):
		pass

	def on_disconnect(self, addr, sock):
		pass

	def on_recv(self, addr, sock, data):
		pass

	def on_error(self, exp):
		#traceback.print_exc()
		logging.error(exp)


class Server(ServerBase):
	def __init__(self, host='localhost', port=9999):
		self.addr = (host, port)
		self.sock = Socket()
		self.sock.setsockopt(pysocket.SOL_SOCKET,  pysocket.SO_REUSEADDR, 1)
		self.sock.setsockopt(pysocket.SOL_SOCKET,  pysocket.SO_KEEPALIVE, 1)
		self.sock.setsockopt(pysocket.IPPROTO_TCP, pysocket.TCP_NODELAY,  1)


	def accept_connection(self, conn, addr):
		try:
			self.on_connect(addr, conn)
			while True:
				data = self.recv(conn)
				if not data: break
				self.on_recv(addr, conn, data)

			self.on_disconnect(addr, conn)
			conn.close()
		except Exception, e:
			self.on_error(e)


	def run(self):
		try:
			# will fail when port as busy, or we don't have rights to bind
			self.sock.bind(self.addr)
			self.sock.listen(pysocket.SOMAXCONN)

			while True:
				sock, addr = self.sock.accept()
				conn = Socket(sock)

				c = threading.Thread(target=self.accept_connection, args=[conn, addr, ])
				c.daemon = True
				c.start()

		except pysocket.error, e:
			self.on_error(e)


	def start(self, timeout=0):
		t = threading.Thread(target=self.run)
		t.daemon = True
		t.start()
		time.sleep(timeout)
		return t


class Client(ServerBase):
	def __init__(self, host='localhost', port=9999):
		self.addr = (host, port)
		self.sock = Socket()


	def send(self, data):
		try:
			self.sock.send(data)
		except Exception, e:
			self.on_error(e)


	def run(self):
		try:
			self.sock.connect(self.addr)
			self.on_connect(self.addr, self.sock)

			while True:
				data = self.recv(self.sock)
				if not data: break
				self.on_recv(self.addr, self.sock, data)

		except pysocket.error, e:
			self.on_error(e)
		finally:
			self.on_disconnect(self.addr, self.sock)
			self.sock.close()


	def start(self, timeout=0):
		t = threading.Thread(target=self.run)
		t.daemon = True
		t.start()
		time.sleep(timeout)
		return t
