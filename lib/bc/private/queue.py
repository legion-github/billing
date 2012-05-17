__version__ = '1.0'

from bc.billing import utils
from bc         import database

def resolve(mtype, tid, arg):
	with database.DBCOnnect() as db:
		r = db.query("SELECT rid,rate"+
		             "  FROM rates"+
		             " WHERE state=%s"+
		             "   AND tariff_id=%s"+
		             "   AND arg=%s",
		             (mtype,tid,arg)).one()
		if not r:
			return (None, None)
		return (r['rid'], r['rate'])


def task_add(mtype, otask):
	with database.DBConnect(primarykey = otask.uuid) as db:
		db.insert(mtype, otask.values)
