"""
Mapping: tariff <--> customer <--> user
"""

import uuid, pymongo
from bc import mongodb

def tm_add(tariff_id, customer_id, user_id):
	""" Adds new mapping record. """

	try:
		res = mongodb.collection('tariffs_map').find_one(
			{
				'customer_id': customer_id,
				'user_id': user_id,
			},
			fields = { '_id': True }
		)
		if res:
			return None

		rid = str(uuid.uuid4())
		mongodb.collection('tariffs_map').insert(
			{
				'_id':         rid,
				'customer_id': customer_id,
				'tariff_id':   tariff_id,
				'user_id':     user_id
			},
			safe = True
		)
	except pymongo.OperationFailure:
		return None
	return rid


def tm_remove(typ, uid):
	""" Removes record by type: record, tariff, customer, user. """

	try:
		if typ not in [ 'record', 'tariff', 'customer', 'user' ]:
			return False

		if typ == 'record':
			typ = ''

		mongodb.collection('tariffs_map').remove(
			{ typ + '_id': uid },
			safe = True
		)
	except pymongo.OperationFailure:
		return False
	return True


def tm_change_tariff(customer_id, tariff_id):
	""" Changes tariff for customer. """

	try:
		mongodb.collection('tariffs_map').update(
			{ 'customer_id': customer_id },
			{ '$set': { 'tariff_id': tariff_id } },
			safe = True,
			multi = True
		)
	except pymongo.OperationFailure:
		return False
	return True


def tm_find(typ, uid, fields = None):
	""" Finds records by type: record, tariff, customer, user. """

	try:
		if typ not in [ 'tariff', 'customer', 'user' ]:
			return None

		if typ == 'record':
			typ = ''

		return list(
			mongodb.collection('tariffs_map').find(
				{ typ + '_id': uid },
				fields = fields
			)
		)
	except pymongo.OperationFailure:
		return None
	return None


def tm_find_one(typ, uid, fields = None):
	ret = tm_find(typ, uid, fields)
	if not ret:
		return None
	return ret[0]
