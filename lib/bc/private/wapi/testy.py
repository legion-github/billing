__version__ = '1.0'

from bc import jsonrpc
from bc import log

LOG = log.logger("wapi.testy")

@jsonrpc.methods.jsonrpc_method(auth=0)
def test(params):
	return jsonrpc.methods.jsonrpc_result({'status':'ok'})
