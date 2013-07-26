#
# wapi_testy.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
# Copyright (c) 2012-2013 by Nikolay Ivanov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#
__version__ = '1.0'

import bc_jsonrpc as jsonrpc
from bc import log

LOG = log.logger("wapi.testy")

@jsonrpc.method(auth=0)
def test(params):
	return jsonrpc.result({'status':'ok'})
