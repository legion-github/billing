import uuid
import bobject
import readonly

from bc import database

class Bill(bobject.BaseObject):
	def __init__(self, data = None):
		self.__values__ = {
			'id':     str(uuid.uuid4()),
			'target': u'',
			'group':  0L,
			'value':  0L,
		}

		if data:
			if 'sync' in data:
				del data['sync']
			self.set(data)
