"""Tier types management"""

import uuid
import pymongo.errors

from c2 import config
from c2 import misc
from c2 import mongodb

from billing import constants
from billing import exceptions
from billing import tariffs_map

def find(tier_type_ids=None, fields=None):
	"""Returns iterator to specied tier types"""

	query = {}
	if tier_type_ids is not None:
		query["_id"] = { "$in": tier_type_ids }

	return mongodb.billing_collection("tier_types").find(query, fields)


def add_one(tier_id, tier_name, replication, description=""):
	"""Add a new tier type to database"""

	tier_type = {
		"tier_id": tier_id,
		"replication": replication,
	}

	if mongodb.billing_collection("tier_types").find_one(tier_type, fields = { '_id': True }):
		raise exceptions.TierTypeExistsError()

	tier_type = {
		"tier_id": tier_id,
		"tier_name": tier_name,
		"replication": replication,
		"description": description,
	}

	while True:
		tier_type["_id"] = misc.generate_id(constants.TIER_TYPE_PREFIX)
		try:
			mongodb.billing_collection("tier_types").insert(tier_type, safe=True)
		except pymongo.errors.DuplicateKeyError:
			collisions += 1
			if collisions >= config.MAX_ID_GENERATION_COLLISIONS:
				raise exceptions.TierTypeError("Unable to generate a unique volume ID.")
		else:
			break

	return tier_type


def rename_one(tier_id, description):
	"""Change description of the existing tier type"""

	rc = mongodb.billing_collection("tier_types").update(
		{ "_id": tier_id },
		{ "$set": { "description": description }},
		safe=True
	)["updatedExisting"]

	if not rc:
		raise exceptions.TierTypeError("Failed to change description of tier type {0}".format(tier_id))


def get(user_id, tier_type_id, embedded = False):
	"""Returns the specified tier type."""

	tier_type = mongodb.billing_collection("tier_types").find_one({
		"_id": tier_type_id })
	
	if tier_type is None or tier_type["_id"] not in _get_user_tier_type_ids(user_id):
		raise exceptions.InvalidTierTypeNotFound()

	if embedded:
		tier_type = to_embedded(tier_type)

	return tier_type


def get_all(user_id, mark_default = False, sort = None):
	"""Returns all tier types for the specified user."""

	tier_types = list(mongodb.billing_collection("tier_types").find({
		"_id": { "$in": _get_user_tier_type_ids(user_id) } }, sort = sort))

	if mark_default:
		default = _get_default_tier_type(tier_types)

		for tier_type in tier_types:
			if tier_type["_id"] == default["_id"]:
				tier_type["default"] = True

	return tier_types


def get_default(user_id, embedded = False):
	"""Returns default tier type for the specified user."""

	tier_types = list(mongodb.billing_collection("tier_types").find({
		"_id": { "$in": _get_user_tier_type_ids(user_id) } }))

	tier_type = _get_default_tier_type(tier_types)

	if embedded:
		tier_type = to_embedded(tier_type)

	return tier_type


def to_embedded(tier_type):
	"""Returns a copy of tier type suitable for embedding to other objects."""

	return {
		"id":          tier_type["_id"] if "_id" in tier_type else tier_type["id"],
		"tier_id":     tier_type["tier_id"],
		"tier_name":   tier_type["tier_name"],
		"replication": tier_type["replication"],
	}


def _get_default_tier_type(tier_types):
	"""Returns default tier type."""

	tier_dict = {}

	for tier_type in tier_types:
		if tier_type["tier_id"] not in tier_dict or not tier_type["replication"]:
			tier_dict[tier_type["tier_id"]] = tier_type

	tier_types = sorted(tier_dict.values(), key = lambda tier_type: tier_type["tier_id"])

	if not tier_types:
		raise exceptions.TierTypeError("There is no default tier type.")

	return tier_types[len(tier_types) / 2]


def _get_user_tier_type_ids(user_id):
	"""Returns tier type IDs available to the specified user."""

	r = tariffs_map.tm_find_one("user", user_id)
	if not r:
		return []

	from billing import tariffs

	tariff = tariffs.get(r['tariff_id'])
	return list(tariff["volume_bytes"])

