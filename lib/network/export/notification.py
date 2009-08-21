from network.exchanges import Exchanges
from network.option.ripe import RIPE

class Answer (dict):
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
		self.router = []
		self.atype = []
		self.group = []
		
		self.filter_routers = []
		self.filter_atypes = []
		self.filter_groups = []

	def parse (self,line):
		try:
			data = line.strip().split('|')
			router,atype,group,asn,announce,policy,src,dest,macro,mail,name = data
		except:
			return False

		self.data.append(data)
		if not router in self.router: self.router.append(router)
		if not atype in self.atype: self.atype.append(group)
		if not group in self.group: self.group.append(group)
		
		return True

	def atype (self):
		return self.atype

	def groups (self):
		return self.group
		
	def routers (self):
		return self.router

	def filter_router (self,routers):
		self.filter_routers = routers
		return self

	def filter_type (self,atypes):
		self.filter_atypes = atypes
		return self

	def filter_group (self,groups):
		self.filter_groups = groups
		return self

	def generate (self,template):
		for data in self.data:
			router,atype,group,asn,announce,policy,src,dest,macro,mail,name = data
			if self.filter_routers and router not in self.filter_routers: continue
			if self.filter_atypes and atype not in self.filter_atypes: continue
			if self.filter_groups and groups not in self.filter_groups: continue
			
			replace = Answer({
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
	