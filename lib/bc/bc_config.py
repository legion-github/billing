from c2 import config

BILLING_PROCESS = 5
BILLING_LOG_LEVEL = "debug"
# Path to pid file
PID_DIR = "/var/run/c2"

def init(develop_mode):
	config.init("bc", develop_mode)

	import bc_config
	config.apply_options(bc_config,
		[( "BILLING_PROCESS",        None, True, True ),
		 ( "BILLING_LOG_LEVEL",      None, False, False)])
