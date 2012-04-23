from c2 import config, constants

from bc.private import deck

from bc.withdraw.addresses import withdraw_addresses
from bc.withdraw.fs        import withdraw_fsobject
from bc.withdraw.fs        import withdraw_fsoperations
from bc.withdraw.instances import withdraw_instance
from bc.withdraw.instances import withdraw_service_monitoring
from bc.withdraw.snapshots import withdraw_snapshot
from bc.withdraw.volumes   import withdraw_volume_v2
from bc.withdraw.volumes   import withdraw_volume_io
from bc.withdraw.traffic   import withdraw_traffic
from bc.withdraw.extenders import withdraw_service_extender

from bc.withdraw.fs        import aggregate_fsoperations
from bc.withdraw.instances import aggregate_instance
from bc.withdraw.volumes   import aggregate_volume_io
from bc.withdraw.traffic   import aggregate_traffic

BC_QUEUES = {}

def register_queue(que_id, **kwargs):
	global BC_QUEUES

	BC_QUEUES[que_id] = {}
	for a in [ 'name', 'withdraw', 'get', 'aggregate', 'describe', 'get_name' ]:
		BC_QUEUES[que_id][a] = kwargs.get(a, None)

#TODO:: id become name,now  name is deprecated field, must be removed
register_queue('billing-instances',
	name      = 'billing-instances',
	withdraw  = withdraw_instance,
	aggregate = aggregate_instance,
	get       = deck.get_task_remove,
	describe  = lambda x:"os_types."+x["ostype"],
	get_name  = lambda x:x["id"],
)
register_queue('billing-service-monitoring',
	name      = 'billing-service-monitoring',
	withdraw  = withdraw_service_monitoring,
	aggregate = aggregate_instance,
	get       = deck.get_task_remove,
	describe  = lambda x:"service.monitoring",
	get_name  = lambda x:x["id"],
)
register_queue('billing-service-extender',
	name      = 'billing-service-extender',
	withdraw  = withdraw_service_extender,
	get       = deck.get_task,
	describe  = lambda x: { constants.EXT_NET_STATE_IDLE:"service.extender.idle",
							constants.EXT_NET_STATE_ATTACHED:"service.extender.attached"}[x["state"]],
	get_name  = lambda x:x["name"]+" "+x["state"],
)
register_queue('billing-fs',
	name      = 'billing-fs',
	withdraw  = withdraw_fsobject,
	get       = deck.get_task,
	describe  = lambda x:"fs.bytes",
	get_name  = lambda x:x["name"],
)
register_queue('billing-fs-ops',
	name      = 'billing-fs-ops',
	withdraw  = withdraw_fsoperations,
	aggregate = aggregate_fsoperations,
	get       = deck.get_task_remove,
	describe  = lambda x:"fs."+x["action"],
	get_name  = lambda x:x["name"],
)
register_queue('billing-volumes-v2',
	name     = 'billing-volumes-v2',
	withdraw = withdraw_volume_v2,
	get      = deck.get_task,
	describe = lambda x:"volume.bytes",
	get_name = lambda x:x["name"],
)
register_queue('billing-volumes-io',
	name      = 'billing-volumes-io',
	withdraw  = withdraw_volume_io,
	aggregate = aggregate_volume_io,
	get       = deck.get_task_remove,
	describe = lambda x:"volume.io",
	get_name = lambda x:x["volume_id"],
)
register_queue('billing-snapshots',
	name     = 'billing-snapshots',
	withdraw = withdraw_snapshot,
	get      = deck.get_task,
	describe = lambda x:"snapshot.bytes",
	get_name = lambda x:x["name"],
)
register_queue('billing-addresses',
	name     = 'billing-addresses',
	withdraw = withdraw_addresses,
	get      = deck.get_task,
	describe = lambda x:"ipaddr.reserve" if x["state"]=="assigned" else "ipaddr.use",
	get_name = lambda x:x["addrs"]+" "+x["state"],
)
register_queue('billing-traffic',
	name      = 'billing-traffic',
	withdraw  = withdraw_traffic,
	aggregate = aggregate_traffic,
	get       = deck.get_task_remove,
	describe  = lambda x:"traffic."+x["type"]+"."+x["direct"],
	get_name  = lambda x:x["ip"] +" "+ x["type"] +" "+ x["direct"],
)

