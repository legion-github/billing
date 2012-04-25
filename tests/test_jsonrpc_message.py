import unittest
from bc.jsonrpc import message

class Test(unittest.TestCase):

	def test_is_response(self):
		"""Check response validation"""

		r0 = {"jsonrpc": "2.0", "result": 19, "id": 3}
		r1 = {"jsonrpc": "2.0", "result": -19, "id": 4}
		r2 = {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request."}, "id": None}
		r3 = {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found."}, "id": "5"}
		r4 = {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}
		r5 = {"foo":"bar"}

		self.assertTrue(message.jsonrpc_is_response(r0))
		self.assertTrue(message.jsonrpc_is_response(r1))
		self.assertTrue(message.jsonrpc_is_response(r2))
		self.assertTrue(message.jsonrpc_is_response(r3))
		self.assertFalse(message.jsonrpc_is_response(r4))
		self.assertFalse(message.jsonrpc_is_response(r5))


	def test_is_response1(self):
		"""Check jsonrpc_is_response incoming argumeng"""
		self.assertFalse(message.jsonrpc_is_response(1))
		self.assertFalse(message.jsonrpc_is_response([]))
		self.assertFalse(message.jsonrpc_is_response(""))


	def test_is_request(self):
		"""Check request validation"""

		r0 = {"jsonrpc": "2.0", "method": "subtract", "params": 123, "id": 1}
		r1 = {"jsonrpc": "2.0", "method": "subtract",                "id": 1}
		r2 = {"jsonrpc": "2.0", "method": "subtract", "params": 123         }
		r3 = {"jsonrpc": "2.0",                       "params": 123, "id": 1}
		r4 = {                  "method": "subtract", "params": 123, "id": 1}
		r5 = {"jsonrpc": "2.0", "method": "subtract", "params": 123, "id": [1,2,3]}
		r6 = {"jsonrpc": "2.0", "method": "subtract", "params": 123, "id": None}

		self.assertTrue(message.jsonrpc_is_request(r0))
		self.assertTrue(message.jsonrpc_is_request(r1))

		self.assertFalse(message.jsonrpc_is_request(r2))
		self.assertFalse(message.jsonrpc_is_request(r3))
		self.assertFalse(message.jsonrpc_is_request(r4))
		self.assertFalse(message.jsonrpc_is_request(r5))
		self.assertFalse(message.jsonrpc_is_request(r6))


	def test_is_request1(self):
		"""Check jsonrpc_is_request incoming argumeng"""
		self.assertFalse(message.jsonrpc_is_request(1))
		self.assertFalse(message.jsonrpc_is_request([]))
		self.assertFalse(message.jsonrpc_is_request(""))


	def test_is_notification(self):
		"""Check notification validation"""

		r0 = {"jsonrpc": "2.0", "method": "subtract", "params": 123, "id": 1}
		r1 = {"jsonrpc": "2.0", "method": "update", "params": [1,2,3,4,5]}
		r2 = {"jsonrpc": "2.0", "method": "foobar"}

		self.assertFalse(message.jsonrpc_is_notification(r0))
		self.assertTrue(message.jsonrpc_is_notification(r1))
		self.assertTrue(message.jsonrpc_is_notification(r2))

	def test_request(self):
		"""Check request creation"""

		a0 = {'jsonrpc': '2.0', 'method': 'foobar', 'id': '123'}
		r0 = message.jsonrpc_request("foobar", None)

		a1 = {'jsonrpc': '2.0', 'method': 'foobar', 'params': [1,2,3], 'id': '123'}
		r1 = message.jsonrpc_request("foobar", [1,2,3])

		a2 = {'jsonrpc': '2.0', 'method': 'foobar', 'params': 'ZZZ', 'id': '123'}
		r2 = message.jsonrpc_request("foobar", "ZZZ")

		self.assertTrue(message.jsonrpc_is_request(r0))
		self.assertTrue(message.jsonrpc_is_request(r1))
		self.assertTrue(message.jsonrpc_is_request(r2))

		self.assertEqual(set(a0.keys()), set(r0.keys()))
		self.assertEqual(set(a1.keys()), set(r1.keys()))
		self.assertEqual(set(a2.keys()), set(r2.keys()))


	def test_notification(self):
		"""Check notify creation"""

		a0 = {'jsonrpc': '2.0', 'method': 'foobar'}
		r0 = message.jsonrpc_notify("foobar", None)

		a1 = {'jsonrpc': '2.0', 'method': 'foobar', 'params': [1,2,3]}
		r1 = message.jsonrpc_notify("foobar", [1,2,3])

		a2 = {'jsonrpc': '2.0', 'method': 'foobar', 'params': 'ZZZ'}
		r2 = message.jsonrpc_notify("foobar", "ZZZ")

		self.assertTrue(message.jsonrpc_is_notification(r0))
		self.assertTrue(message.jsonrpc_is_notification(r1))
		self.assertTrue(message.jsonrpc_is_notification(r2))

		self.assertEqual(set(a0.keys()), set(r0.keys()))
		self.assertEqual(set(a1.keys()), set(r1.keys()))
		self.assertEqual(set(a2.keys()), set(r2.keys()))


	def test_response(self):
		"""Check response creation"""

		req = message.jsonrpc_request("foobar", None)
		res = message.jsonrpc_response(req, {'status':'ok'})

		self.assertTrue(message.jsonrpc_is_response(res))
		self.assertEqual(req['id'], res['id'])


	def test_response_error(self):
		"""Check error response"""

		req = message.jsonrpc_request("foobar", None)

		res = message.jsonrpc_response_error(req, 'InvalidRequest', {'status':'fail'})
		self.assertTrue(message.jsonrpc_is_response(res))
		self.assertEqual(req['id'], res['id'])
		self.assertEqual(res['error']['code'], -32600)

		res = message.jsonrpc_response_error(req, 'FooBar', {'status':'fail'})
		self.assertTrue(message.jsonrpc_is_response(res))
		self.assertEqual(req['id'], res['id'])
		self.assertEqual(res['error']['code'], -32603)

		res = message.jsonrpc_response_error(req, None, {'status':'fail'})
		self.assertTrue(message.jsonrpc_is_response(res))
		self.assertEqual(req['id'], res['id'])
		self.assertEqual(res['error']['code'], -32603)
