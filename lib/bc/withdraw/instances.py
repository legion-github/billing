from bc.private.rate import Rate
from bc.private      import deck
from bc              import bc_common as common

def withdraw_instance(task, nostate=False):
	data      = task[deck.DATA]
	user      = task[deck.USER]
	customer  = task[deck.CUSTOMER]
	tariff_id = task[deck.TARIFF]
	tariff    = common.get_tariff(tariff_id)
	os_type   = data['ostype']

	cost = Rate(0)

	rate = Rate(tariff['os_types'][os_type]['rate'])
	if rate == 0:
		return (None, None)

	cost += rate * int(data['usetime'])

	return (customer, cost)


def withdraw_service_monitoring(task, nostate=False):
	data      = task[deck.DATA]
	user      = task[deck.USER]
	customer  = task[deck.CUSTOMER]
	tariff_id = task[deck.TARIFF]
	tariff    = common.get_tariff(tariff_id)

	cost = Rate(0)
	rate = Rate(tariff['service']['monitoring']['rate'])
	if rate == 0:
		return (None, None)

	cost += rate * int(data['usetime'])

	return (customer, cost)


def aggregate_instance(task):
	deck.aggregate_daily(
		task,
		id_data = [
			task[deck.TARIFF],
			task[deck.CUSTOMER],
			task[deck.USER],
			task[deck.DATA]['uuid'],
			task[deck.DATA]['ostype'],
		],
		more = {
			'$set': {
				deck.DATA + '.uuid':   task[deck.DATA]['uuid'],
				deck.DATA + '.ostype': task[deck.DATA]['ostype'],
				deck.DATA + '.id':     task[deck.DATA]['id'],
			},
			'$inc': {
				deck.DATA + '.usetime': task[deck.DATA]['usetime']
			}
		}
	)
