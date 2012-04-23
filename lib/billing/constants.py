MAX_RATE = 33
"""Maximum rate value."""

PRICE_PRECISION = 100
"""To convert dollars to cents."""

HOUR_SECONDS = 60 * 60
"""Seconds in the hour"""

DAY_SECONDS = HOUR_SECONDS * 24
"""Seconds in the day"""

MONTH_SECONDS = 30 * 24 * HOUR_SECONDS
"""Seconds in the month. We assume that month has 30 days."""


CURRENCY_LIST = [
	"RUB", # Russian Ruble
	"USD", # US Dollar
	"EUR"  # Euro
]
"""List of supported currencies"""

WALLET_MODE_LIMITED   = "limited"
WALLET_MODE_UNLIMITED = "unlimited"

BC_QUEUES = [
	'billing-instances',
	'billing-service-monitoring',
	'billing-fs-ops',
	'billing-fs',
	'billing-snapshots',
	'billing-volumes-v2',
	'billing-volumes-io',
	'billing-addresses',
	'billing-traffic',
	'billing-service-monitoring'
]
"""All available billing queues"""

TIER_TYPE_PREFIX = "tier-"
"""Tier type's id prefix."""
