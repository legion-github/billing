import hashlib

from decimal import Decimal, getcontext

from c2 import constants as c2_constants

from billing import constants as billing_constants

RATE_COEFFICIENT = billing_constants.PRICE_PRECISION * (10 ** billing_constants.MAX_RATE)
GB_MONTH_COEFFICIENT = c2_constants.GIGABYTE * billing_constants.MONTH_SECONDS


def sha1(*args):
	data = ""
	for a in args:
		data += str(a) + "-"
	return hashlib.sha1(data).hexdigest()


def dict_merge(*args):
	"""
	Merge dicts and store result into first argument.
	Example:
	python> res = {}
	python> dict_merge(res, dict1, dict2, dict3)
	"""
	def _merge(r, d):
		for k,v in d.iteritems():
			if k in r:
				if isinstance(v, dict):
					_merge(r[k], v)
					continue
			r[k] = v
		return r
	return reduce(_merge, args)


def extended_precision(func):
	"""Run function with extended decimal precision"""

	def decorator(*args, **kwargs):
		oldprec = getcontext().prec
		getcontext().prec = billing_constants.MAX_RATE + 3
		try:
			return func(*args, **kwargs)
		finally:
			getcontext().prec = oldprec

	return decorator


def _dividend(value):
	"""Make divident for all fractions"""

	return int(Decimal(value) * RATE_COEFFICIENT)


@extended_precision
def gb_month_to_rate(value):
	"""Converts GB-month to Byte-sec and return an appropriate rate"""

	return str(_dividend(value) // GB_MONTH_COEFFICIENT)


@extended_precision
def rate_to_gb_month(rate):
	"""Converts rate to GB-month"""

	return str((Decimal(rate) * GB_MONTH_COEFFICIENT) / RATE_COEFFICIENT)


@extended_precision
def count_to_rate(counter, value):
	"""Converts "per count" to appropriate rate"""

	return str(_dividend(value) // counter)


@extended_precision
def rate_to_count(counter, rate):
	"""Converts rate to "per count" price"""

	return str((Decimal(rate) * counter) / RATE_COEFFICIENT)


@extended_precision
def month_to_rate(value):
	"""Converts month to sec and return an appropriate rate"""

	return str(_dividend(value) // billing_constants.MONTH_SECONDS)


@extended_precision
def rate_to_month(rate):
	"""Converts rate Month"""

	return str((Decimal(rate) * billing_constants.MONTH_SECONDS) / RATE_COEFFICIENT)


@extended_precision
def hour_to_rate(value):
	"""Converts hour to sec and return an appropriate rate"""

	return str(_dividend(value) // billing_constants.HOUR_SECONDS)


@extended_precision
def rate_to_hour(rate):
	"""Converts rate Hour"""

	return str((Decimal(rate) * billing_constants.HOUR_SECONDS) / RATE_COEFFICIENT)


@extended_precision
def gb_to_rate(value):
	"""Converts GB to Byte and return an appropriate rate"""

	return str(_dividend(value) // c2_constants.GIGABYTE)


@extended_precision
def rate_to_gb(rate):
	"""Converts rate to GB"""

	return str((Decimal(rate) * c2_constants.GIGABYTE) / RATE_COEFFICIENT)


@extended_precision
def rate_to_money(rate):
	"""Converts rate to money"""

	return str(Decimal(rate) / RATE_COEFFICIENT)
