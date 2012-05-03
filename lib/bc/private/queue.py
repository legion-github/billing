__version__ = '1.0'

from bc.billing import utils
from bc         import mongodb

def resolve(mtype, tid, arg):
	# Use sha1(mtype, tid, arg) to get shard id.
	r = mongodb.collection('rates').find_one(
		{
			'mtype': mtype,
			'tid':   tid,
			'arg':   arg
		}
	)
	if not r:
		return (None, None)
	return (r['rid'], r['rate'])


def task_add(mtype, otask):
	mongodb.collection(mtype, otask.uuid).insert(otask.values, safe=True)
