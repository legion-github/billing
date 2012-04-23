from c2 import core

class TariffNotFoundError(core.EC2Error):
	def __init__(self):
		super(TariffNotFoundError, self).__init__("TariffNotFound", "Tariff not found")


class InvalidTariffValueError(core.EC2Error):
	def __init__(self, message=None):
		super(InvalidTariffValueError, self).__init__("InvalidTariffValue", message or "Tariff contains invalid value")


class IncompatibleTariffError(core.EC2Error):
	def __init__(self, message=None):
		super(IncompatibleTariffError, self).__init__("IncompatibleTariff", message or "It is impossible to change the tariff for the incompatible")


class TierTypeError(core.EC2Error):
	def __init__(self, message=None):
		super(TierTypeError, self).__init__("TierTypeError", message)


class TierTypeExistsError(core.EC2Error):
	def __init__(self):
		super(TierTypeExistsError, self).__init__("TierTypeExists", "Specified tier type already exists")


class InvalidTierTypeNotFound(core.EC2Error):
	def __init__(self):
		super(InvalidTierTypeNotFound, self).__init__("InvalidTierType.NotFound", "Specified tier type does not exist")
