import unittest

from bc.jsonrpc import message
from c2.tests2 import utils


class JsonRpcTest(unittest.TestCase):

	def test_is_response(self):
		"""jsonrpc_is_response(message)"""

		r = {"jsonrpc": "2.0", "result": 19, "id": 3}
		self.assertTrue(message.jsonrpc_is_response(r))

		r = {"jsonrpc": "2.0", "result": -19, "id": 4}
		self.assertTrue(message.jsonrpc_is_response(r))

		r = {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request."}, "id": None}
		self.assertTrue(message.jsonrpc_is_response(r))

		r = {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found."}, "id": "5"}
		self.assertTrue(message.jsonrpc_is_response(r))

		r = {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}
		self.assertFalse(message.jsonrpc_is_response(r))

		r = {"foo":"bar"}
		self.assertFalse(message.jsonrpc_is_response(r))


	def test_is_response1(self):
		"""jsonrpc_is_response(trash)"""
		self.assertFalse(message.jsonrpc_is_response(1))
		self.assertFalse(message.jsonrpc_is_response([]))
		self.assertFalse(message.jsonrpc_is_response(""))


if __name__ == '__main__':
	utils.run_tests(JsonRpcTest)
