import client


def Customers(host, auth, timeout):
	return client.BCClient(host, auth, timeout, [
		'customerList',
		'customerGet',
		'customerAdd',
		'customerModify',
		'customerRemove',
		'customerIdRemove',
		'customerDeposit',
		])


def Metrics(host, auth, timeout):
	return client.BCClient(host, auth, timeout, [
		'metricList',
		'metricAdd',
		'metricGet',
		])


def Rates(host, auth, timeout):
	return client.BCClient(host, auth, timeout, [
		'rateList',
		'rateGet',
		'rateAdd',
		'rateModify',
		'rateRemove',
		])


def Tariffs(host, auth, timeout):
	return client.BCClient(host, auth, timeout, [
		'tariffList',
		'tariffGet',
		'tariffAdd',
		'tariffAddInternal',
		'tariffModify',
		'tariffRemove',
		'tariffIdRemove',
		])


def Tasks(host, auth, timeout):
	return client.BCClient(host, auth, timeout, [
		'taskAdd',
		'taskModify',
		'taskRemove',
		])

