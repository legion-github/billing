import hashlib

class HashRing(object):
	def __init__(self, nodes=list(), replicas=3):
		"""
		Manages a hash ring.

		`nodes` is a list of objects that have a proper __str__ representation.
		`replicas` indicates how many virtual points should be used pr. node,
		replicas are required to improve the distribution.
		"""

		self.nodes = dict()
		self.ring  = dict()
		self._sorted_keys = []

		for node in nodes:
			self.add_node(node, replicas) 


	def gen_key(self, key):
		"""
		Given a string key it returns a long value,
		this long value represents a place on the hash ring.
		"""

		return long(hashlib.sha1(key).hexdigest(), 16)


	def add_node(self, node, replicas=3):
		"""Adds a `node` to the hash ring (including a number of replicas)."""

		for i in xrange(0, replicas):
			key = self.gen_key('%s:%s' % (node, i))
			self.ring[key] = node
			self._sorted_keys.append(key)

		self.nodes[node] = { 'replicas': replicas }
		self._sorted_keys.sort()


	def remove_node(self, node):
		"""Removes `node` from the hash ring and its replicas."""

		if node not in self.nodes:
			return

		for i in xrange(0, self.nodes[node].replicas):
			key = self.gen_key('%s:%s' % (node, i))
			del self.ring[key]
			self._sorted_keys.remove(key)

		del self.nodes[node]


	def get_node_pos(self, string_key):
		"""
		Given a string key a corresponding node in the hash ring is returned
		along with it's position in the ring.
		If the hash ring is empty, (`None`, `None`) is returned.
		"""

		if not self.ring:
			return None, None

		key = self.gen_key(string_key)

		for i in xrange(0, len(self._sorted_keys)):
			node = self._sorted_keys[i]

			if key <= node:
				return self.ring[node], i

		return self.ring[self._sorted_keys[0]], 0


	def get_node(self, string_key):
    		"""
    		Given a string key a corresponding node in the hash ring is returned.
		If the hash ring is empty, `None` is returned.
		"""

		return self.get_node_pos(string_key)[0]


	def get_nodes(self, string_key):
		"""
		Given a string key it returns the nodes as a generator that can hold the key.
		The generator is never ending and iterates through the ring
		starting at the correct position.
		"""

		if not self.ring:
			yield None, None

		node, pos = self.get_node_pos(string_key)
		for key in self._sorted_keys[pos:]:
			yield self.ring[key]

		while True:
			for key in self._sorted_keys:
				yield self.ring[key]


