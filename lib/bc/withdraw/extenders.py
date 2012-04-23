from c2 import constants

from bc.private.rate import Rate
from bc.private      import deck
from bc              import bc_common as common


def withdraw_service_extender(task, nostate=False):
	data      = task[deck.DATA]
	user      = task[deck.USER]
	customer  = task[deck.CUSTOMER]
	tariff_id = task[deck.TARIFF]
	tariff    = common.get_tariff(tariff_id)

	if int(task[deck.TIME_DESTROY]) > 0:
		delta_ts = int(task[deck.TIME_DESTROY]) - int(task[deck.TIME_CHECK])
		if not nostate:
			deck.state_done(task)
	else:
		delta_ts = int(task[deck.TIME_NOW]) - int(task[deck.TIME_CHECK])

	if delta_ts < 0:
		delta_ts = 0

	cost = Rate(0)
	rate = Rate(0)

	if   data['state'] == constants.EXT_NET_STATE_IDLE:
		rate = Rate(tariff['service']['extender']['idle']['rate'])
	elif data['state'] == constants.EXT_NET_STATE_ATTACHED:
		rate = Rate(tariff['service']['extender']['attached']['rate'])

	if rate == 0:
		return (None, None)

	cost += rate * delta_ts

	return (customer, cost)
