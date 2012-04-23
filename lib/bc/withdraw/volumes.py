from bc.private.rate import Rate
from bc.private      import deck
from bc              import bc_common as common

def withdraw_volume_v3(task, nostate=False):
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
	rate = Rate(tariff['volume_bytes'][data['tier']]['rate'])
	if rate == 0:
		return (None, None)

	cost += rate * delta_ts * int(data['size'])

	return (customer, cost)


def withdraw_volume_v2(task, nostate=False):
	data      = task[deck.DATA]
	user      = task[deck.USER]
	customer  = task[deck.CUSTOMER]
	tariff_id = task[deck.TARIFF]
	tariff    = common.get_tariff(tariff_id)

	if 'tier' in data:
		return withdraw_volume_v3(task, nostate)

	if int(task[deck.TIME_DESTROY]) > 0:
		delta_ts = int(task[deck.TIME_DESTROY]) - int(task[deck.TIME_CHECK])
		if not nostate:
			deck.state_done(task)
	else:
		delta_ts = int(task[deck.TIME_NOW]) - int(task[deck.TIME_CHECK])

	if delta_ts < 0:
		delta_ts = 0

	cost = Rate(0)
	rate = Rate(tariff['volume']['bytes']['rate'])
	if rate == 0:
		return (None, None)

	cost += rate * delta_ts * int(data['size'])

	return (customer, cost)


def withdraw_volume_io(task, nostate=False):
	data      = task[deck.DATA]
	user      = task[deck.USER]
	customer  = task[deck.CUSTOMER]
	tariff_id = task[deck.TARIFF]
	tariff    = common.get_tariff(tariff_id)

	cost = Rate(0)
	rate = Rate(tariff['volume']['io']['requests']['rate'])
	if rate == 0:
		return (None, None)

	cost += rate * int(data['requests'])

	return (customer, cost)


def aggregate_volume_io(task):
	deck.aggregate_daily(
		task,
		id_data = [
			task[deck.TARIFF],
			task[deck.CUSTOMER],
			task[deck.USER],
			task[deck.DATA]['instance_uuid'],
			task[deck.DATA]['volume_uuid']
		],
		more = {
			'$set': {
				deck.DATA + '.instance_id':   task[deck.DATA]['instance_id'],
				deck.DATA + '.instance_uuid': task[deck.DATA]['instance_uuid'],
				deck.DATA + '.volume_id':     task[deck.DATA]['volume_id'],
				deck.DATA + '.volume_uuid':   task[deck.DATA]['volume_uuid'],
			},
			'$inc': {
				deck.DATA + '.requests': task[deck.DATA]['requests']
			}
		}
	)
