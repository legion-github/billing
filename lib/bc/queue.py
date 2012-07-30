__version__ = '1.0'

from bc import database
from bc import rates

def resolve(mtype, tid):
	"""Rate information by tariff and metric"""

	with database.DBConnect() as db:
		r = db.find_one('rates',
			{
				'state':     rates.constants.STATE_ACTIVE,
				'mtype':     mtype,
				'$or': [
					{ 'tariff_id': tid },
					{ 'tariff_id': '*' }
				]
			},
			fields=['rid','rate']
		)
		if not r:
			return (None, None)
		return (r['rid'], r['rate'])
