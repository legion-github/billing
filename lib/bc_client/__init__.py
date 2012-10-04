import client

def configcreator(hosts_auth, local, method_returning):
	"""For lazy administrators with same auth on diffrent wapis"""
	ans = {}
	for key,value in method_returning.iteritems():
		ans[key]={
			'local': local,
			'hosts': hosts_auth,
			'returning': value
			}
	return ans


def Client(config):
	"""
	config sample:
	{
	...
	'wapiMethodName': {
		'returning': 'returningData',
		'hosts': {
			'HOST1:PORT':{
				"role": "admin",
				"secret": "qwerty"
			},
			'HOST2:PORT':{
				"role": "user",
				"secret": "123456"
			},
		},
		'local': 'HOST1:PORT'
		},
	...
	}
	"""
	return client.BCClient(config)


def Customers(hosts_auth, local):
	return client.BCClient(configcreator(
		hosts_auth, local,
		{
			'customerList':    'customers',
			'customerGet':     'customer',
			'customerAdd':     'id',
			'customerModify':  'status',
			'customerRemove':  'status',
			'customerDeposit': 'status',
		}))


def Metrics(hosts_auth, local):
	return client.BCClient(configcreator(
		hosts_auth, local,
		{
		'metricList':'metrics',
		'metricAdd': 'id',
		'metricGet': 'metric',
		}))


def Rates(hosts_auth, local):
	return client.BCClient(configcreator(
		hosts_auth, local,
		{
		'rateList':  'rates',
		'rateGet':   'rate',
		'rateAdd':   'id',
		'rateModify':'status',
		'rateRemove':'status',
		}))


def Tariffs(hosts_auth, local):
	return client.BCClient(configcreator(
		hosts_auth, local,
		{
		'tariffList':       'tariffs',
		'tariffGet':        'tariff',
		'tariffAdd':        'id',
		'tariffModify':     'status',
		'tariffRemove':     'status',
		}))


def Tasks(hosts_auth, local):
	return client.BCClient(configcreator(
		hosts_auth, local,
		{
		'taskAdd':   'id',
		'taskModify':'status',
		'taskRemove':'status',
		}))

def Sync(hosts_auth, local):
	return client.BCClient(configcreator(
		hosts_auth, local,
		{
		'sync':    'status',
		'syncList':'status',
		}))
