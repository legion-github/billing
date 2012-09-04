import client


def Customers(host, auth, timeout):
	return client.BCClient(host, auth, timeout, [
		('customerList',    'customers'),
		('customerGet',     'customer'),
		('customerAdd',     'id'),
		('customerModify',  'status'),
		('customerRemove',  'status'),
		('customerIdRemove','status'),
		('customerDeposit', 'status'),
		])


def Metrics(host, auth, timeout):
	return client.BCClient(host, auth, timeout, [
		('metricList','metrics'),
		('metricAdd', 'id'),
		('metricGet', 'metric'),
		])


def Rates(host, auth, timeout):
	return client.BCClient(host, auth, timeout, [
		('rateList',  'rates'),
		('rateGet',   'rate'),
		('rateAdd',   'id'),
		('rateModify','status'),
		('rateRemove','status'),
		])


def Tariffs(host, auth, timeout):
	return client.BCClient(host, auth, timeout, [
		('tariffList',       'tariffs'),
		('tariffGet',        'tariff'),
		('tariffAdd',        'id'),
		('tariffAddInternal','id'),
		('tariffModify',     'status'),
		('tariffRemove',     'status'),
		('tariffIdRemove',   'status'),
		])


def Tasks(host, auth, timeout):
	return client.BCClient(host, auth, timeout, [
		('taskAdd',   'id'),
		('taskModify','status'),
		('taskRemove','status'),
		])

