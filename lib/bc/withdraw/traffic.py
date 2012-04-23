from bc.private.rate import Rate
from bc.private      import deck
from bc              import bc_common as common

def withdraw_traffic(task, nostate=False):
	data      = task[deck.DATA]
	user      = task[deck.USER]
	customer  = task[deck.CUSTOMER]
	tariff_id = task[deck.TARIFF]
	tariff    = common.get_tariff(tariff_id)

	traf_type   = data['type']
	traf_direct = data['direct']
	traf_bytes  = data['bytes']

	cost = Rate(0)
	rate = Rate(tariff['traffic'][traf_type][traf_direct]['rate'])
	if rate == 0:
		return (None, None)

	cost += rate * int(traf_bytes)

	return (customer, cost)


def aggregate_traffic(task):
	deck.aggregate_daily(
		task,
		id_data = [
			task[deck.TARIFF],
			task[deck.CUSTOMER],
			task[deck.USER],
			task[deck.DATA]['type'],
			task[deck.DATA]['direct'],
			task[deck.DATA]['ip']
		],
		more = {
			'$set': {
				deck.DATA + '.ip':     task[deck.DATA]['ip'],
				deck.DATA + '.type':   task[deck.DATA]['type'],
				deck.DATA + '.direct': task[deck.DATA]['direct'],
				deck.DATA + '.owner':  task[deck.DATA]['owner'],
				deck.DATA + '.time':   0,
			},
			'$inc': {
				deck.DATA + '.bytes': task[deck.DATA]['bytes']
			}
		}
	)
