__version__ = '1.0'

from bc import database
from bc import rates

def resolve(mtype, tid):

	with database.DBCOnnect() as db:
		r = db.find_one('rates',
			{
				'state':     rates.constants.STATE_ACTIVE,
				'mtype':     mtype,
				'tariff_id': tid,
			},
			fields=['rid','rate']
		)
		if not r:
			return (None, None)
		return (r['rid'], r['rate'])
