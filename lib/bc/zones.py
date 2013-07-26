#
# zones.py
#
# Copyright (c) 2012-2013 by Alexey Gladkov
#
# This file is covered by the GNU General Public License,
# which should be included with billing as the file COPYING.
#
from bc import config
from bc import hashing

def write_zone(key):
	conf = config.read()
	data = config.subdict(conf['zones'], field='weight')
	ring = hashing.HashRing(data.keys(), data)
	res  = ring.get_node(key)
	return conf['zones'][res]
