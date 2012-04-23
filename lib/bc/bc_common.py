from billing import tariffs

tariff_cache = {}

def get_tariff(tariff_id):
	global tariff_cache

	if tariff_id not in tariff_cache:
		tariff_cache[tariff_id] = tariffs.get(tariff_id)

	return tariff_cache[tariff_id]
