import unithelper
import random
import string

from bc_client.client import BCClient
from bc_client.client import BillingError
from unithelper import mocker

class Test(unithelper.TestCase):

	def test_BCClient_init(self):
		"""Check creaing billing client object"""
		method_list = [''.join(random.choice(string.ascii_letters) for x in xrange(10)) for y in xrange(random.randint(5,15))]
		a = BCClient('host','auth','timeout',method_list)

		self.assertEquals(set(dir(a)), set(dir(object) + method_list + [
			'__dict__',
			'__module__',
			'__weakref__',
			'_BCClient__request']))


	def test_BCClient_exceptions(self):
		"""Check exceptions"""
		with mocker([('httplib.HTTPConnection', mocker.exception),
			('bc_client.client.LOG.error', mocker.passs)]):
			a = BCClient('host','auth','timeout',['a'])
			with self.assertRaises(Exception):
				a.a()


		with mocker([
			('bc_jsonrpc.http.jsonrpc_http_request',
				lambda *args, **kwargs: {'error':{'code':-32001}}),
			('httplib.HTTPConnection',
				lambda *a, **k: mocker.mockclass(connect=mocker.passs) ),
			('bc_client.client.LOG.error',
				mocker.passs)]):
			a = BCClient('host','auth','timeout',['a'])
			with self.assertRaises(BillingError):
				a.a()





