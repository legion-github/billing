from bc.private.rate import Rate
from bc.private      import deck
from bc              import bc_common as common

def withdraw_fsobject(task, nostate=False):
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
	rate = Rate(tariff['fs']['bytes']['rate'])
	if rate == 0:
		return (None, None)

	cost += rate * delta_ts * int(data['size'])

	return (customer, cost)


def withdraw_fsoperations(task, nostate=False):
	data      = task[deck.DATA]
	user      = task[deck.USER]
	customer  = task[deck.CUSTOMER]
	tariff_id = task[deck.TARIFF]
	tariff    = common.get_tariff(tariff_id)

	cost = Rate(0)

	rate = Rate(tariff['fs'][data['action']]['rate'])
	if rate == 0:
		return (None, None)

	if 'count' in data:
		cost += rate * int(data['count'])

	return (customer, cost)


def aggregate_fsoperations(task):

	if 'count' in task[deck.DATA]:
		num = int(task[deck.DATA]['count'])
	else:
		num = 1

	deck.aggregate_daily(
		task,
		id_data = [
			task[deck.TARIFF],
			task[deck.CUSTOMER],
			task[deck.USER],
			task[deck.DATA]['uuid'],
		],
		more = {
			'$set': {
				deck.DATA + '.uuid': task[deck.DATA]['uuid'],
				deck.DATA + '.name': task[deck.DATA]['name'],
				deck.DATA + '.action': task[deck.DATA]['action'],
			},
			'$inc': {
				deck.DATA + '.count': num
			}
		}
	)
