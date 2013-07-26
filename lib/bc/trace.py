#
# trace.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#
"""
The module contains a decorator to keep track of function calls. The decorator is controlled via environment variables^

USE_TRACE     - activates the module;
TRACE_STACK   - turn on tracing functions calls that marked by decorator;
TRACE_LONG_ID - variable forces to the use of long identifiers;
TRACE_GROUP   - trace only functions marked by specified group and ungrouped functions.

"""

__all__ = [ "trace" ]

import os, uuid, logging, string

use_trace      = bool(int(os.environ.get("USE_TRACE",     0)))
trace_stack    = bool(int(os.environ.get("TRACE_STACK",   0)))
trace_short_id = bool(int(os.environ.get("TRACE_LONG_ID", 0)))

call_stack = []

def trace(level = "info", log_name = "c2.trace", group = None):
	"""
	Decorator to trace function call with sspeficied logging level.
	Arguments:

	level - logging level (debug, warning, error, info, ...);
	log_name - logger name;
	group - functions group.

	"""

	def __trace_timing_level(func):
		""" Internal decorator to trace function """

		if not use_trace:
			return func

		trace_group = os.environ.get("TRACE_GROUP", "")

		if group and trace_group and group != trace_group:
			return func

		def wrapper(*args, **kwargs):
			""" Trace wrapper """

			LOG = logging.getLogger(log_name)
			call_id = uuid.uuid4().hex

			if trace_short_id:
				call_id = call_id[:8]

			try:
				stack = ""
				if trace_stack:
					stack = ", stack=[" + string.join(call_stack, ", ") + "]"

				getattr(LOG, level)(
					"TRACE: %s: Call func=%s, args=%s, kwargs=%s%s",
					call_id, func.__name__, args, kwargs, stack
				)

				if trace_stack:
					call_stack.append(call_id + ":" + func.__name__)

				# Run target function with given arguments
				ret = func(*args, **kwargs)

				getattr(LOG, level)(
					"TRACE: %s: Return func=%s, return=%s",
					call_id, func.__name__, ret
				)
			except Exception, e:
				getattr(LOG, level)(
					"TRACE: %s: Exception func=%s, except=%s(%s)",
					call_id, func.__name__, type(e).__name__, e
				)
				raise e
			finally:
				if trace_stack:
					call_stack.pop()
			return ret
		return wrapper
	return __trace_timing_level
