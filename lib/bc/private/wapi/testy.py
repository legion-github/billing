__version__ = '1.0'

from bc import jsonrpc

@jsonrpc.methods.jsonrpc_method(auth=0)
def test(params):
	return jsonrpc.methods.jsonrpc_result({'status':'ok'})
