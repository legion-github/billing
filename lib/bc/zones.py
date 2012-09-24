#!/usr/bin/python

from bc import config
from bc import hashing
from bc import database

from bc import customers
from bc import metrics
from bc import rates
from bc import tariffs


def write_zone(key):
	conf = config.read()
	data = config.subdict(conf['zone'], field='weight')
	ring = hashing.HashRing(data.keys(), data)
	res  = ring.get_node(key)
	return conf['zone'][res] 


def sync_record(table, params):

	SYNC_TABLES = {
		'customers': customers.Customer,
		'metrics':   metrics.Metric,
		'rates':     rates.Rate,
		'tariffs':   tariffs.Tariff
	}

	if table not in SYNC_TABLES:
		raise ValueError("Not synchronizable table")

	o = SYNC_TABLES[table](params)

	with database.DBConnect() as db:
		try:
			db.insert(table, o.values)
			return

		except OperationalError, e:
			if e.pgcode != 23505:
				raise
			# Ignore duplicate key value violates unique constraint
			pass

		db.update(table, { 'id': o.id }, o.values)
