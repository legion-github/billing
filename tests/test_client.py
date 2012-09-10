import unithelper
import random
import string

from bc_client.client import BCClient
from bc_client.client import BillingError
from unithelper import mocker

class Test(unithelper.TestCase):

	def test_BCClient_init(self):
		"""Check creaing billing client object"""
		method_list = dict([(''.join(random.choice(string.ascii_letters) for x in xrange(10)), 'status') for y in xrange(random.randint(5,15))])
		with mocker([
			('httplib.HTTPConnection',
				lambda *a, **k: mocker.mockclass(connect=mocker.passs) )]):
			a = BCClient('host','auth','timeout',method_list)

		self.assertEquals(set(dir(a)), set(dir(object) + method_list.keys() + [
			'__dict__',
			'__module__',
			'__weakref__',
			'_BCClient__request',
			'conn',
			]))

	def test_BCClient_exceptions(self):
		"""Check exceptions"""
		with mocker([('httplib.HTTPConnection', mocker.exception),
			('bc_client.client.LOG.error', mocker.passs)]):
			with self.assertRaises(Exception):
				BCClient('host','auth','timeout',{'a':'status'})

		with mocker([
			('bc_jsonrpc.http.jsonrpc_http_request',
				lambda *args, **kwargs: {'error':{'code':-32001}}),
			('httplib.HTTPConnection',
				lambda *a, **k: mocker.mockclass(connect=mocker.passs) ),
			('bc_client.client.LOG.error',
				mocker.passs)]):
			with self.assertRaises(BillingError):
				BCClient('host','auth','timeout',{'a':'status'}).a()


