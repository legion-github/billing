__version__ = '1.0'

from bc.validator import Validate as V
from bc import jsonrpc
from bc import log
from bc import customers

LOG = log.logger("wapi.customers")


@jsonrpc.methods.jsonrpc_method(validate = False, auth = True)
def customerList(request):
	""" Returns a list of all registered customers """

	try:
		ret = map(lambda c: c.values, customers.get_all())
	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to obtain customer list'
			}
		)
	return jsonrpc.methods.jsonrpc_result(
		{
			'status':'ok',
			'metrics': ret
		}
	)


@jsonrpc.methods.jsonrpc_method(
	validate = V({
		'login':            V(basestring, max=64),
		'name_short':       V(basestring, max=255),
		'name_full':        V(basestring, required=False, max=1024),
		'comment':          V(basestring, required=False, max=1024),
		'contact_person':   V(basestring, required=False, min=2, max=255),
		'contact_email':    V(basestring, required=False, max=255),
		'contact_phone':    V(basestring, required=False, max=30),
		'wallet':           V(int       , required=False),
		'wallet_mode':      V(int       , required=False),
		'tariff_id':        V(basestring, required=False, min=36, max=36),
		'contract_client':  V(basestring, required=False, max=255),
		'contract_service': V(basestring, required=False, max=255),
	}),
	auth = True)
def customerAdd(params):
	""" Adds new customer account """

	try:
		c = customers.Customer(params)
		customers.add(c)

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to add new customer'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })


@jsonrpc.methods.jsonrpc_method(
	validate = V({ 'login': V(basestring, min=1, max=64) }),
	auth = True)
def customerRemove(params):
	""" Remove customer by name """

	try:
		c = customers.remove('login', params['login'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to remove customer'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })


@jsonrpc.methods.jsonrpc_method(
	validate = V({ 'id': V(basestring, min=36, max=36) }),
	auth = True)
def customerIdRemove(params):
	""" Remove customer by id """

	try:
		c = customers.remove('id', params['id'])

	except Exception, e:
		LOG.error(e)
		return jsonrpc.methods.jsonrpc_result_error('ServerError',
			{
				'status':  'error',
				'message': 'Unable to remove customer'
			}
		)
	return jsonrpc.methods.jsonrpc_result({ 'status':'ok' })
