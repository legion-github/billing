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
