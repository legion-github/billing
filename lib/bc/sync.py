#!/usr/bin/python
#
# sync.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
# Copyright (c) 2012-2013 by Nikolay Ivanov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#

from bc import database

from bc import bills
from bc import customers
from bc import metrics
from bc import rates
from bc import tariffs


def record(table, params):

	SYNC_TABLES = {
		'customerbills': bills.Bill,
		'customers':     customers.Customer,
		'metrics':       metrics.Metric,
		'rates':         rates.Rate,
		'tariffs':       tariffs.Tariff
	}

	if table not in SYNC_TABLES:
		raise ValueError("Not synchronizable table")

	o = SYNC_TABLES[table](params)

	with database.DBConnect() as db:
		try:
			db.insert(table, o.values)
			return

		except database.DatabaseError, e:
			if e.pgcode != '23505':
				raise
			# Ignore duplicate key value violates unique constraint
			pass

		db.update(table, { 'id': o.id }, o.values)
