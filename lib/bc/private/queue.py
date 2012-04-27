__version__ = '1.0'

from bc.billing import utils
from c2 import mongodb

def resolve(self, mtype, tid, arg):
	# Use sha1(mtype, tid, arg) to get shard id.
	r = mongodb.billing_collection('rates').find_one(
		{
			'mtype': mtype,
			'tid':   tid,
			'arg':   arg
		}
	)
	if not r:
		return (None, None)
	return (r['rid'], r['rate'])

