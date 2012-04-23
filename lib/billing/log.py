import logging, time
from c2 import mongodb

LOG = logging.getLogger("c2.bc.log")

def deposit(customer, ammount):
	try:
		mongodb.billing_collection("log_deposit").insert(
			{
				'date': int(time.time()),
				'customer': customer,
				'ammount': ammount
			}
		)
	except Exception, e:
		LOG.exception("Unable to update deposit log: %s, customer=%s, ammount=%s",
		              e, repr(customer), repr(ammount))


def user(uobj):
	mongodb.billing_collection("log_accounts").insert(
		{
			'date': int(time.time()),
			'customer': uobj['owner'],
			'user': uobj['uuid'],
			'name': uobj['name']
		}
	)
