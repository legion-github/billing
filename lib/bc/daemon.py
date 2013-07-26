#
# daemon.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
# Copyright (c) 2012-2013 by Nikolay Ivanov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#
import os
import sys
import errno
import fcntl
import signal
import stat
import resource


class PidFileError(Exception):
	def __init__(self, error, *args):
		Exception.__init__(self,
			error.format(*args) if len(args) else str(error))


class PidFileLocked(PidFileError):
	"""Raised when we attempt to lock an already locked PID file."""
	def __init__(self):
		super(PidFileError, self).__init__(self,
			"The PID file is already locked by another process.")


def _syscall_wrapper(func, *args, **kwargs):
	"""Calls func() ignoring EINTR error."""

	while True:
		try:
			return func(*args, **kwargs)
		except EnvironmentError as e:
			if e.errno != errno.EINTR:
				raise


def close_all_fds(skipfd=[]):
	fd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]

	if fd == resource.RLIM_INFINITY:
		fd = 1024

	while fd >= 0:
		try:
			if fd not in skipfd:
				os.close(fd)
		except:
			pass
		fd -= 1

	null_dev = _syscall_wrapper(os.open, "/dev/null", os.O_RDWR)
	try:
		for fd in [ sys.stdin.fileno(), sys.stdout.fileno(), sys.stderr.fileno() ]:
			if fd in skipfd:
				continue
			os.dup2(null_dev, fd)
	finally:
		_syscall_wrapper(os.close, null_dev)


def daemonize(nofork=False, nochdir=False, noclose=False, skipfd=[]):
	"""Daemonizes current process."""

	if not nofork:
		if os.fork():
			os._exit(0)
		else:
			os.setsid()

			if os.fork():
				os._exit(0)

	if not nochdir:
		os.chdir("/")
	os.umask(0)

	signal.signal(signal.SIGHUP, signal.SIG_IGN)
	signal.siginterrupt(signal.SIGHUP, False)

	# Redirecting stdout and stderr to the /dev/null and closing the original stdin.
	if not noclose:
		close_all_fds(skipfd)


def acquire_pid(pid_file):
	"""Open and lock pidfile"""

	fd = -1

	try:
		fd = _syscall_wrapper(os.open, pid_file, os.O_RDWR | os.O_CREAT, 0600)

		if fd <= sys.stderr.fileno():
			_syscall_wrapper(os.dup2, fd, sys.stderr.fileno() + 1)
			_syscall_wrapper(os.close, fd)
			fd = sys.stderr.fileno() + 1

		try:
			fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
		except EnvironmentError as e:
			if e.errno == errno.EWOULDBLOCK:
				raise PidFileLocked()
			raise e

		fd_stat = os.fstat(fd)

		try:
			file_stat = os.stat(pid_file)
		except EnvironmentError as e:
			if e.errno == errno.ENOENT:
				raise PidFileLocked()
			raise e

		if ((  fd_stat[stat.ST_DEV],  fd_stat[stat.ST_INO]) !=
		    (file_stat[stat.ST_DEV],file_stat[stat.ST_INO])):
			raise PidFileLocked()
		return fd

	except PidFileLocked:
		if fd != -1: _syscall_wrapper(os.close, fd)
		raise
	except Exception as e:
		if fd != -1: _syscall_wrapper(os.close, fd)
		raise PidFileError("Failed to lock the pidfile: {0}.", e)


def write_pid(fd):
	"""Write pid to pidfile previously allocated by acquire_pid()"""

	data = str(os.getpid())
	datalen = len(data)

	while data:
		size = _syscall_wrapper(os.write, fd, data)
		data = data[size:]

	os.ftruncate(fd, datalen)
	os.fchmod(fd, 0644)
