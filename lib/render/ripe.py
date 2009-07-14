from netaddr import IP,CIDR

from twisted.internet import reactor

class Whois (object):
	def __init__ (self,range,host='whois.ripe.net',port=43):
		self.rpsl = RPSL(range)
		reactor.connectTCP(host, port, _RIPEClientFactory(self.rpsl,range))
		reactor.run()

class RPSL (object):
	def __init__ (self,range):
		self.range = range
		self.nb24s = pow(2,32-CIDR(range).prefixlen) >> 8

		self.inetnum = {}
		self.key = ''
		self.data = ''
		self.errors = []

	def dataReceived (self,data):
		self.data += data

	def complete (self):
		for line in self.data.split('\n'):
			if line == '': continue
			if line.startswith('%'): continue
			try:
				key, value = line.split(':',1)
			except ValueError:
				raise

			key = key.lower().strip()
			if key == 'inetnum':
				s,e = value.strip().replace(' ','').split('-',1)
				self.key,end = IP(s),IP(e)
				if self.inetnum.has_key(self.key):
					print >> sys.stderr, 'duplicate key %s' % self.key
				self.inetnum[self.key] = {}

				self.inetnum[self.key]['start'] =  IP(self.key)
				self.inetnum[self.key]['end'] = IP(end)
				self.inetnum[self.key]['length'] = IP(end).value - IP(self.key).value + 1

			if self.inetnum[self.key].has_key(key):
				self.inetnum[self.key][key].append(value.strip())
			else:
				self.inetnum[self.key][key] = [value.strip()]

	def __str__ (self):
		r = ''
		for k in self.inetnum.keys():
			r += '\n'
			for k,vs in self.inetnum[k].iteritems():
				for v in vs:
					r += '%-12s %s\n' % ('%s:' % k, v)
		return r


	def fragment (self):
		per24 = {}

		for key in self.inetnum.keys():
			ip1,ip2,ip3,_ = tuple(key)
			c = IP('.'.join([str(i) for i in (ip1,ip2,ip3,0)]))
			try:
                		per24[c].append(key)
			except KeyError:
				per24[c] = [key]
				
		return per24


from twisted.internet.protocol import Protocol, ClientFactory

class _RIPEProtocol(Protocol):
	def connectionMade (self):
		self.transport.write('-B -r -T inetnum -M %s\n' % self.factory.range)

	def dataReceived(self, data):
		self.factory.dataReceived(data)


class _RIPEClientFactory(ClientFactory):
	def __init__ (self,container,range):
		self.container = container
		self.range = range

	def buildProtocol(self, addr):
		ripe = _RIPEProtocol()
		ripe.factory = self
		return ripe

	def clientConnectionLost(self, connector, reason):
		reactor.stop()
		self.container.complete()

	def dataReceived (self,data):
		self.container.dataReceived(data)

