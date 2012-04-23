import time
import re

import pymongo
import pymongo.errors

import uuid
import logging

from c2 import constants
from c2 import limits
from c2 import mongodb
from c2 import passwords

from billing import tariffs
from billing import tariffs_map
from billing import constants as b_constants
from billing import exceptions as b_exceptions

from c2.aws import exceptions

### global variables

__LOG = logging.getLogger("c2.wallets")

DEFAULT_CREATE_TIME = 1303128000 # Mon Apr 18 12:00:00 UTC 2011

TARIFF_STATE_APPLIED  = 'applied'
TARIFF_STATE_UPDATING = 'updating'

PUBLIC_PROPERTIES = [
	"_id",
	"name",
	"description",
	"contact_name",
	"contact_email",
	"status",
	"password_expires",
	"contract",
	"tariff",
	"tariff_prev",
	"tariff_name",
	"tariff_currency",
	"tariff_status",
	"wallet",
	"wallet_mode"

]

__UNITS = [
	'credit-0',  # kop        / sec  1
	'credit-3',  # kop*10^-03 / sec  2
	'credit-6',  # kop*10^-06 / sec  3
	'credit-9',  # kop*10^-09 / sec  4 
	'credit-12', # kop*10^-12 / sec  5
	'credit-15', # kop*10^-15 / sec  6
	'credit-18', # kop*10^-18 / sec  7
	'credit-21', # kop*10^-21 / sec  8
	'credit-24', # kop*10^-24 / sec  9
	'credit-27', # kop*10^-27 / sec  10
	'credit-30', # kop*10^-30 / sec  11
	'credit-33'  # kop*10^-33 / sec  12
]

__ULLONG_MAX = (1L << 64) - 1
__UNITS_LEN  = len(__UNITS) - 1
__UNITS_RANK = 1000
__UNITS_AGE  = 100


### utilities

def _extern_customer(obj, ignore_wallets=False):
	"""Returns external representation of customer object"""

	response = {}
	for p in PUBLIC_PROPERTIES:
		response[p] = obj.get(p)

	response["create_time"] = str(obj.get("create_time", DEFAULT_CREATE_TIME))

	if not ignore_wallets:
		response["wallet"] = obj.get("wallet")
		response["negative_balance"] = obj.get("wallet_mode") == b_constants.WALLET_MODE_UNLIMITED

	return response


def _denormalize_tariff(tariff):
	"""Prepare query to change tariff related fields"""

	return {
		"tariff": tariff["_id"],
		"tariff_name": tariff["name"],
		"tariff_currency": tariff["currency"]
	}


def _get_db_customer(customer_id, required=False):
	"""Get customer's entry from database (find by arbitrary field)"""

	obj = mongodb.billing_collection("customers").find_one({"_id": customer_id})

	if required and not obj:
			raise exceptions.CustomerNotFoundError()

	return obj


def _value(customer_id):
	"""Get value of customer's wallet"""

	obj = get(customer_id)
	if not obj: return 0

	v = obj["wallet"]
	if v <= 0 and obj.get("wallet_mode") == b_constants.WALLET_MODE_UNLIMITED:
		v = 1

	return v


def _credit_sync(customer_id, credit):
	"""Made deposit operation on internal Rate object.
	   This object is represented by set of 'credit-*' fields inside wallet document."""

	i = __UNITS_LEN
	while i > 0:
		value = credit[__UNITS[i]]
		if value >= __UNITS_RANK:
			n = value // __UNITS_RANK
			c = mongodb.billing_collection("customers").find_and_modify(
				{
					'_id': customer_id,
					__UNITS[i]: {'$gte':   n * __UNITS_RANK}
				},
				{
					'$inc': {
						__UNITS[i]:  -n * __UNITS_RANK,
						__UNITS[i-1]: n
					},
					'$set': {'age': 0}
				},
				new = True
			)
			if c:
				if c[__UNITS[i]] < 0:
					__LOG.error("{0}: Credit {1} was overflowed by {2} !".format(customer_id, __UNITS[i], (n * __UNITS_RANK)))
				else:
					credit = c
		i -= 1
	return credit


def _wallet_decrement(customer_id, ammount):
	"""Made withdraw operation on customer's wallet"""

	try:
		mongodb.billing_collection("customers").update(
			{
				'_id': customer_id,
				__UNITS[0]: {'$gte': ammount}
			},
			{
				'$inc': {
					'wallet': -ammount,
					__UNITS[0]: -ammount
				}
			},
			safe = True)

	except Exception, e:
		raise Exception("Unable to decrement wallet: {0}: {1}: {2}".format(customer_id, ammount, e))

### management API

def generate_password():
	"""Returns a newly generated password"""

	return passwords.gen_password()


def add(new_obj, **defaults):
	"""Add a new customer"""

	# verify customer's name against system policy
	name = new_obj["name"]
	if not (
		isinstance(name, basestring) and
		1 < len(name) < limits.MAX_CUSTOMER_NAME_LENGTH and
		re.match(r"^[a-zA-Z0-9_.-]*$", name)
	):
		raise exceptions.InvalidCustomerNameError()

	tariff = tariffs.get(new_obj["tariff"])

	# prepare new database entry
	query = {
		"_id": str(uuid.uuid4()),
		"name": name,
		"contact_name": new_obj.get("contact_name", ""),
		"contact_email": new_obj.get("contact_email", ""),
		"status": constants.CUSTOMER_STATUS_ENABLED,
		"contract": new_obj.get("contract", "0000"),
		"description": new_obj.get("description", ""),
		"create_time": int(time.time()),
		"password": "",
		"password_expires": 0L,
		"tags":[],
		"tariff_prev": "",
		"tariff_status": TARIFF_STATE_APPLIED,
		"wallet": 0L,
		"wallet_mode": b_constants.WALLET_MODE_UNLIMITED if new_obj.get("negative_balance") else b_constants.WALLET_MODE_LIMITED,
	}

	for k in __UNITS:
		query[k] = 0L

	query.update(_denormalize_tariff(tariff)) # apply tariff
	query.update(passwords.hsh_password(name, new_obj.get("password"))) # apply password
	query.update(defaults) # override defaults

	# insert new customers's entry to database
	try:
		coll = mongodb.billing_collection("customers")
		coll.insert(query, safe = True)
	except pymongo.errors.DuplicateKeyError:
		raise exceptions.CustomerAlreadyExistsError()

	return query


def get(customer_id, ignore_wallets=False):
	"""Get customer properties (find by uuid)"""

	obj = _get_db_customer(customer_id, required=True)
	return _extern_customer(obj)


def login(customer_name, customer_password):
	"""Check customer via name and password"""

	obj = mongodb.billing_collection("customers").find_one({"name": customer_name})
	if not obj:
			raise exceptions.CustomerNotFoundError()

	if not passwords.cmp_password(customer_password, obj["password"]):
		raise exceptions.AuthFailure()

	if obj["status"] != constants.CUSTOMER_STATUS_ENABLED:
		raise exceptions.AuthFailure()

	return obj["_id"]


def set(new_obj):
	"""Modify customer properties (find by uuid)"""

	obj = _get_db_customer(new_obj["_id"], required = True)

	if obj["status"] == constants.CUSTOMER_STATUS_DELETED:
		raise exceptions.CustomerNotFoundError()

	if obj["_id"] == constants.ADMIN_CUSTOMER_ID:
		return

	# prepare query
	query = {}
	if ("status" in new_obj) and (new_obj["status"] in constants.CUSTOMER_STATUSES):
		query["status"] = new_obj["status"]

	for option in [ "contact_name", "contact_email", "contract", "description" ]:
		if option in new_obj:
			query[option] = new_obj[option]
	query.update(passwords.hsh_password(obj["name"], new_obj.get("password")))

	if "negative_balance" in new_obj:
		 query["wallet_mode"] = b_constants.WALLET_MODE_UNLIMITED if new_obj["negative_balance"] else b_constants.WALLET_MODE_LIMITED

	# apply changes
	rc = mongodb.billing_collection("customers").update({"_id": obj["_id"]}, {"$set": query}, safe=True)
	if not rc["updatedExisting"]:
		raise exceptions.CustomerNotFoundError()


def set_tariff_applied(customer_id):
	mongodb.billing_collection("customers").update(
		{
			"_id": customer_id,
			"tariff_status": TARIFF_STATE_UPDATING
		},
		{ "$set": {
			"tariff_status": TARIFF_STATE_APPLIED }
		}
	)


def set_tariff(customer_id, tariff_id):
	"""Change customer's tariff"""

	obj = _get_db_customer(customer_id, required = True)
	new_tariff = tariffs.get_child(tariff_id, obj["tariff"])

	if not new_tariff:
		raise b_exceptions.IncompatibleTariffError()

	action = _denormalize_tariff(new_tariff)
	action['tariff_prev'] = obj['tariff']
	action['tariff_status'] = TARIFF_STATE_UPDATING

	rc = mongodb.billing_collection("customers").update(
		{
			"_id": obj["_id"],
			"tariff_status": TARIFF_STATE_APPLIED
		},
		{ "$set": action },
		safe=True
	)
	if not rc["updatedExisting"]:
		raise exceptions.CustomerTariffLockedError()

	# FIXME: check return code
	tariffs_map.tm_change_tariff(customer_id, tariff_id)


def rollback_tariff(customer_id):
	"""Try to rollback customer's tariff"""

	obj = _get_db_customer(customer_id, required = True)
	old_tariff = tariffs.get_parent(obj["tariff"])

	if not old_tariff:
		raise b_exceptions.IncompatibleTariffError()

	action = _denormalize_tariff(old_tariff)
	action['tariff_prev'] = obj['tariff']
	action['tariff_status'] = TARIFF_STATE_UPDATING

	rc = mongodb.billing_collection("customers").update(
		{
			"_id": obj["_id"],
			"tariff_status": TARIFF_STATE_APPLIED
		},
		{ "$set": action },
		safe=True
	)
	if not rc["updatedExisting"]:
		raise exceptions.CustomerTariffLockedError()


def get_all(status=None, ignore_wallets=False):
	"""List available customers"""

	query = {}

	if status:
		query["status"] = { "$in": status }

	response = []
	for obj in mongodb.billing_collection("customers").find(query, sort = [("name", pymongo.ASCENDING)]):
		if obj['_id'] == constants.ADMIN_CUSTOMER_ID:
			continue

		if not status and obj['status'] == constants.CUSTOMER_STATUS_DELETED:
			continue

		response.append(_extern_customer(obj, ignore_wallets))

	return response


def deposit(customer_id, ammount):
	"""Make deposit to customer"""
	if not isinstance(ammount, (int, long)) or ammount < 0:
		raise exceptions.InvalidParameterValue("Invalid ammount value")

	if customer_id != constants.ADMIN_CUSTOMER_ID:
		result = mongodb.billing_collection("customers").update(
			{
				"_id": customer_id
			},
			{
				"$inc": { "wallet": ammount }
			},
			safe=True
			)["updatedExisting"]

		if not result:
			raise exceptions.InvalidParameterValue("Failed to make deposit to customer")


def delete(customer_id):
	"""Remove customer without depends (for internal use only)"""

	mongodb.billing_collection("customers").remove({'_id': customer_id})

	# At the time of removal of customer, all users have already been removed.
	# This is just insurance.
	tariffs_map.tm_remove("customer", customer_id)


def validate_wallet(customer_id):
	"""Validate customer's wallet"""

	return _value(customer_id) > 0

def withdraw(customer_id, rate):
	"""Withdraw money from customer's wallet"""

	if customer_id == constants.ADMIN_CUSTOMER_ID:
		return

	customer_ammount = rate.export(units = 12, inc = 3)

	# Check for value > 1L
	if customer_ammount[0] > __ULLONG_MAX:
		raise Exception("Unable to withdraw value > 1L: customerid={0}".format(customer_id))

	credit_ammount = {'age': 0}

	for i in customer_ammount:
		if customer_ammount[i]:
			credit_ammount['age'] += 1

		credit_ammount['credit-' + str(i)] = customer_ammount[i]

	if credit_ammount['age'] == 0:
		return

	credit = mongodb.billing_collection("customers").find_and_modify(
			{'_id': customer_id},
			{'$inc': credit_ammount},
			new = True)

	if credit['age'] < __UNITS_AGE:
		i = __UNITS_LEN
		while i > 0:
			if credit[__UNITS[i]] >= (100 * __UNITS_RANK):
				credit = _credit_sync(customer_id, credit)
				break
			i -= 1
	else:
		credit = _credit_sync(customer_id, credit)

	if credit[__UNITS[0]] > 0:
		_wallet_decrement(customer_id, credit[__UNITS[0]])
