#!/usr/bin/python

from bc import config
from bc import hashing


def write_zone(key):
	conf = config.read()
	data = config.subdict(conf['zone'], field='weight')
	ring = hashing.HashRing(data.keys(), data)
	res  = ring.get_node(key)
	return conf['zone'][res] 
