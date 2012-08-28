import hashlib
import string


def sha1(*args):
	data = map(lambda x: str(x), args)
	return hashlib.sha1(string.join(data, '-') + '-').hexdigest()


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
			if not isinstance(v, (int,long,basestring,unicode)):
				r[k] = v.__class__(v)
			else:
				r[k] = v
		return r
	return reduce(_merge, args)
