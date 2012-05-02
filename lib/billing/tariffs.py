#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import sys
import copy
import logging
import pymongo
import time
import uuid
import hashlib

from c2 import misc
from bc import mongodb
from c2 import instances
from c2 import constants as c_constants

from billing import tier_types as b_tier_types
from billing import constants as b_constants
from billing import utils as b_utils
from billing import exceptions as b_exceptions
from billing import tier_types

__LOG = logging.getLogger("c2.tariffs")

# Все 'rate' указаны в соответствии со значением '10^-33' копейки
TARIFF_TEMPLATE = {
	'create_time': 0,
	'_id':         '',
	'name':        '',
	'description': '',
	'currency':    '',
	'state': 'enable',
	'vm_types': {
#		"m1_small":  { "cpu": 1, "memory": 1073741824 },
#		"m1_medium": { "cpu": 2, "memory": 2147483648 },
#		"m1_large":  { "cpu": 4, "memory": 4294967296 },
	},
	'os_types': {
#		"ef6e560a-423d-4304-b20f-5596657d2bc5": { "vm_type": "m1.small",  "os": "linux",   "rate": "4" },
#		"2d89f850-2831-4e90-aa9c-6d3a9c8f0763": { "vm_type": "m1.medium", "os": "generic", "rate": "4" },
#		"2agggggg-2831-4e90-aa9c-6d3a9c8f0763": { "vm_type": "m1.large",  "os": "generic", "rate": "4" },
	},
	'fs': {
		'bytes': { 'rate': '0' },   # Цена за 1 байт
		'get':   { 'rate': '0' },   # Стоимость одного GET
		'put':   { 'rate': '0' } }, # Стоимость одного PUT
	'snapshot': {
		'bytes': { 'rate': '0' } },   # Цена за 1 байт
	'volume_bytes': { # Стоимость хранения самого volume в секунду.
#		"dd236772": { 'rate': '0' },
#		"3555b9db": { 'rate': '0' },
	},
	'ipaddr': {
		# Стоимость секунды использования IP
		'reserve': { 'rate': '0' },   # Цена зарезервированного IP
		'use':     { 'rate': '0' } }, # Цена назначенного IP (используемого)
	'traffic': {
		'region': {
			'incoming': { 'rate': '0' },
			'outgoing': { 'rate': '0' } },
		'external': {
			'incoming': { 'rate': '0' },
			'outgoing': { 'rate': '0' } } },
	'service': {
		'monitoring':  { 'rate': '0' } }
}

### utilities

def _base_verify(t, path):
	"""Checks basic tarriff syntax aka all integer values must be greater than 0"""
	keys = t.keys()
	prefix = ""
	if len(path) > 0:
		prefix = path + "."

	for n in keys:
		if   type(t[n]) == dict:
			_base_verify(t[n], prefix + n)

		elif type(t[n]) == int:
			if int(t[n]) < 0:
				raise b_exceptions.InvalidTariffValueError('Value should be 0 or greater: ' + prefix + n)

		elif type(t[n]) == str:
			if len(t[n]) == 0:
				raise b_exceptions.InvalidTariffValueError('Value should not be empty: ' + prefix + n)

		if n == 'currency':
			if t[n] not in b_constants.CURRENCY_LIST:
				raise b_exceptions.InvalidTariffValueError('Value should in list: ' + repr(b_constants.CURRENCY_LIST))

def _verify(tariff, strict = True):
	"""Made tariff verification"""

	_base_verify(tariff, "")

	if not strict:
		return

	fields = {
		'vm_types':     'Instance types',
		'os_types':     'OS platforms',
		'volume_bytes': 'Volume bytes',
	}

	for k,desc in fields.iteritems():
		if not tariff[k]:
			raise b_exceptions.InvalidTariffValueError(desc + ' not specified')

	generic_found = False
	for key, os_type in tariff['os_types'].iteritems():
		if os_type['os'] == c_constants.TEMPLATE_OS_DEFAULT:
			generic_found = True
			break

	if not generic_found:
		raise b_exceptions.InvalidTariffValueError('Generic platform not specified')


def _cell_id(type_id, os_id):
	"""Calculate unique hash value for cell.
	   We are using hash to provide a same hash for same combination of os type an vm type"""

	line = misc.get_utf8_value(instances.vm_type_user_to_db(type_id) + "-" + os_id)
	return hashlib.sha1(line).hexdigest()

### public API

def get(uuid):
	"""Returns specified tariff"""

	if uuid is None:
		raise b_exceptions.TariffNotFoundError()

	tariff = mongodb.collection("tariffs").find_one({'_id': uuid})
	if not tariff:
		raise b_exceptions.TariffNotFoundError()
	return tariff

def get_all():
	"""Returns all available tariffs"""

	res = []
	for t in mongodb.collection("tariffs").find():
		if t['_id'] != c_constants.ADMIN_TARIFF_ID:
			res.append(t)
	return res

def get_subtree_iter(tariff_id):
	"""Returns iterator to traverse tariff's subtree"""

	for child in mongodb.collection("tariffs").find({"parent": tariff_id}):
		yield child
		for subchild in get_subtree_iter(child["_id"]):
			yield subchild


def get_child(tariff_id, parent_id):
	"""Returns new tariff if it is child of current tariff"""

	new_tariff = get(tariff_id)
	current_tariff = new_tariff
	while True:
		if not current_tariff.get("parent"):
			return None

		if current_tariff["parent"] == parent_id:
			return new_tariff

		current_tariff = get(current_tariff["parent"])

def is_compatible(tariff1, tariff2):
	"""Tariffs are compatible if and only if their OS sets are equal"""

	return \
		set(tariff1["os_types"].keys())     == set(tariff2["os_types"].keys()) and \
		set(tariff1["volume_bytes"].keys()) == set(tariff2["volume_bytes"].keys())

def get_parent(tariff_id):
	"""Returns previous tariff if OS set of current tariff equals to OS set of a previous one"""

	tariff = get(tariff_id)
	parent = get(tariff.get("parent"))

	return parent if is_compatible(tariff, parent) else None

def create(values, uid=None, strict_check=True):
	tariff = copy.deepcopy(TARIFF_TEMPLATE)
	tariff.update(values)

	tariff['_id']  = uid if uid else str(uuid.uuid4())
	tariff['create_time'] = int(time.time())

	_verify(tariff, strict_check)

	coll = mongodb.collection("tariffs")
	coll.insert(tariff)

	return tariff['_id']


def remove(uuid, real=None):
	coll = mongodb.collection("tariffs")

	tariff = coll.find_one({'_id': uuid})
	if not tariff:
		raise b_exceptions.TariffNotFoundError()

	if real:
		coll.remove({'_id': uuid})
		return

	tariff['state'] = 'disable'
	coll.save(tariff)

def extern_vmtypes(dct):
	"""Returns external representation of vm types"""

	result = [
		{
			"name": t.replace("_","."),
			"cpu": dct[t]["cpu"],
			"ccus": dct[t]["ccus"],
			"memory": dct[t]["memory"] // c_constants.MEGABYTE
		}
		for t in dct
	]

	result.sort(cmp = lambda x, y:
		cmp(float(x["ccus"]), float(y["ccus"])) or
		cmp(x["cpu"], y["cpu"]) or
		cmp(x["memory"], y["memory"])
	)

	return result


def extern_tiertypes(obj):
	"""Returns external representation of tier types"""

	res = []
	for t in tier_types.find(obj['volume_bytes'].keys()).sort("tier_id"):
		t['id'] = t['_id']
		del t['_id']
		t['rate'] = b_utils.rate_to_gb_month(obj["volume_bytes"][t['id']]["rate"])
		res.append(t)
	return res


def extern_ostypes(dct):
	"""Returns external representation of os types"""

	cache = {}

	for cell in dct.itervalues():
		os = cell["os"]
		p = cache.setdefault(os, { "name": os, "rates": {} })
		p["rates"][cell["vm_type"].replace("_",".")] = b_utils.rate_to_hour(cell["rate"])

	return cache.values()


def extern_tariff(obj):
	"""Returns external representation of tariff"""

	return {
		"uuid":	obj["_id"],
		"name": obj["name"],
		"description": obj["description"],
		"currency": obj["currency"],

		"fs_bytes": b_utils.rate_to_gb_month(obj["fs"]["bytes"]["rate"]),
		"fs_put": b_utils.rate_to_count(1000, obj["fs"]["put"]["rate"]),
		"fs_get": b_utils.rate_to_count(10000, obj["fs"]["get"]["rate"]),

		"snapshot_bytes": b_utils.rate_to_gb_month(obj["snapshot"]["bytes"]["rate"]),

		"ipaddr_reserve": b_utils.rate_to_month(obj["ipaddr"]["reserve"]["rate"]),
		"ipaddr_use": b_utils.rate_to_month(obj["ipaddr"]["use"]["rate"]),

		"traffic_region_incoming": b_utils.rate_to_gb(obj["traffic"]["region"]["incoming"]["rate"]),
		"traffic_region_outgoing": b_utils.rate_to_gb(obj["traffic"]["region"]["outgoing"]["rate"]),

		"traffic_external_incoming": b_utils.rate_to_gb(obj["traffic"]["external"]["incoming"]["rate"]),
		"traffic_external_outgoing": b_utils.rate_to_gb(obj["traffic"]["external"]["outgoing"]["rate"]),

		"service_monitoring": b_utils.rate_to_hour(obj["service"]["monitoring"]["rate"]),

		"vm_types": extern_vmtypes(obj["vm_types"]),
		"os_types": extern_ostypes(obj["os_types"]),
		"tiers": extern_tiertypes(obj)
	}

def intern_vmtypes(lst):
	"""Returns internal representation of vm types"""

	return dict( (
		instances.vm_type_user_to_db(t["name"]),
		{
			"cpu":    t["cpu"],
			"ccus":   t["ccus"],
			"memory": t["memory"] * c_constants.MEGABYTE
		}
	) for t in lst)

def intern_ostypes(lst):
	"""Returns internal representation of platforms"""

	return dict((
		_cell_id(t, o["name"]),
		{
			"os":      o["name"],
			"vm_type": instances.vm_type_user_to_db(t),
			"rate":    b_utils.hour_to_rate(o["rates"][t])
		}
	) for o in lst for t in o["rates"] if o["rates"][t])

def intern_tiertypes(lst):
	"""Returns internal representation of volume_bytes"""

	return dict((
		t["id"],
		{
			'rate': b_utils.gb_month_to_rate(t['rate']),
		}
	) for t in lst)

def intern_tariff(obj):
	"""Returns internal representation of tariff"""

	res = {
		"parent": obj.get("parent", ""),
		"name": obj["name"],
		"description": obj["description"],
		"currency": obj["currency"],
		"fs": {
			"bytes": { "rate": b_utils.gb_month_to_rate(obj["fs_bytes"]) },
			"put": { "rate": b_utils.count_to_rate(1000, obj["fs_put"]) },
			"get": { "rate": b_utils.count_to_rate(10000, obj["fs_get"]) }
		},
		"snapshot": {
			"bytes": { "rate": b_utils.gb_month_to_rate(obj["snapshot_bytes"]) },
		},
		"ipaddr": {
			"reserve": { "rate": b_utils.month_to_rate(obj["ipaddr_reserve"]) },
			"use": { "rate": b_utils.month_to_rate(obj["ipaddr_use"]) }
		},
		"traffic": {
			"external": {
				"incoming": { "rate": b_utils.gb_to_rate(obj["traffic_external_incoming"]) },
				"outgoing": { "rate": b_utils.gb_to_rate(obj["traffic_external_outgoing"]) }
			},
			'region': {
				'incoming': { 'rate': '0' },
				'outgoing': { 'rate': '0' }
			}
		},
		"service": {
			"monitoring": { "rate": b_utils.hour_to_rate(obj["service_monitoring"]) }
		},
		"volume_bytes": intern_tiertypes(obj["tiers"]),
		"vm_types": intern_vmtypes(obj["vm_types"]),
		"os_types": intern_ostypes(obj["os_types"]),
	}

	return res

def describe_ostypes(tariff_id, os_type):
	"""return os name and vm_type"""
	os_type = get(tariff_id).get("os_types").get(os_type)
	return os_type["os"], os_type["vm_type"]


def rename_tariff(tariff_id, name, description):
	"""Change tariff's name and description"""

	rc = mongodb.collection("tariffs").update(
		{ "_id": tariff_id },
		{ "$set": { "name": name, "description": description }},
		safe=True
	)["updatedExisting"]

	if not rc:
		raise Exception("Failed to change tariff's name and description")