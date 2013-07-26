#
# __init__.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
# Copyright (c) 2012-2013 by Nikolay Ivanov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#
from client import BCClient


def Customers(auth, server):
	return BCClient(
		{
			'customerList':    'customers',
			'customerGet':     'customer',
			'customerAdd':     'id',
			'customerModify':  'status',
			'customerRemove':  'status',
			'customerDeposit': 'status',
		}, auth, server)


def Metrics(auth, server):
	return BCClient(
		{
		'metricList':'metrics',
		'metricAdd': 'id',
		'metricGet': 'metric',
		}, auth, server)


def Rates(auth, server):
	return BCClient(
		{
		'rateList':  'rates',
		'rateGet':   'rate',
		'rateAdd':   'id',
		'rateModify':'status',
		'rateRemove':'status',
		}, auth, server)


def Tariffs(auth, server):
	return BCClient(
		{
		'tariffList':       'tariffs',
		'tariffGet':        'tariff',
		'tariffAdd':        'id',
		'tariffModify':     'status',
		'tariffRemove':     'status',
		}, auth, server)


def Tasks(auth, server):
	return BCClient(
		{
		'taskAdd':   'id',
		'taskModify':'status',
		'taskRemove':'status',
		}, auth, server)

def Sync(auth, server):
	return BCClient(
		{
		'sync':    'status',
		'syncList':'status',
		}, auth, server)
