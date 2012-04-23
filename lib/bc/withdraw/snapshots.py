from bc.private.rate import Rate
from bc.private      import deck
from bc              import bc_common as common

def withdraw_snapshot(task, nostate=False):
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
	rate = Rate(tariff['snapshot']['bytes']['rate'])
	if rate == 0:
		return (None, None)

	cost += rate * delta_ts * int(data['size'])

	return (customer, cost)

