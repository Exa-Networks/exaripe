from network.exchanges import Exchanges
from network.option.ripe import RIPE

class _Answer (dict):
	def __getitem__ (self,name):
		try:
			return dict.__getitem__(self,name)
		except KeyError:
			return "%s unspecified" % name

class Notification (object):
	def __init__ (self):
		self.exchanges = Exchanges()
		self.ripe = RIPE()
		self.index = 0
		self.data = []
		
		self._filter_router = []
		self._filter_relation = []
		self._filter_group = []

	def parse (self,line):
		try:
			data = line.strip().split('|')
			router,relation,group,asn,announce,policy,src,dest,macro,mail,name = data
		except:
			return False
		
		for response in data:
			if not response:
				# XXX: Mean that we could not find all the info for the peer ...
				return True
		
		self.data.append(data)
		return True
	
	def _filtered (self):
		for data in self.data:
			router,relation,group,asn,announce,policy,src,dest,macro,mail,name = data
			if self._filter_router and router not in self._filter_router: continue
			if self._filter_relation and relation not in self._filter_relation: continue
			if self._filter_group and group not in self._filter_group: continue
			yield data
	
	def routers (self):
		routers = []
		for data in self._filtered():
			if not data[0] in routers: routers.append(data[0])
		return routers
	
	def relations (self):
		relations = []
		for data in self._filtered():
			if not data[1] in relations: relations.append(data[1])
		return relations
	
	def groups (self):
		groups = []
		for data in self._filtered():
			if not data[2] in groups: groups.append(data[2])
		return groups
	
	def filter_router (self,routers):
		self._filter_router = routers
		return self
	
	def filter_relation (self,relations):
		self._filter_relation = relations
		return self
	
	def filter_group (self,groups):
		self._filter_group = groups
		return self
	
	def generate (self,template):
		for data in self._filtered():
			router,relation,group,asn,announce,policy,src,dest,macro,mail,name = data
			
			replace = _Answer({
				'router': router,
				'our_ip': src,
				'your_ip': dest,
				'our_asn' : "AS%s" % self.ripe['asn'],
				'your_asn' : "AS%s" % asn,
				'peer_name': name,
				'exchange': self.exchanges.name(dest),
				'company': self.ripe['company']
			})
			
			message = template.message() % replace
			subject = template.subject() % replace
			yield self.ripe['sender'],mail,subject,message,asn,name
	