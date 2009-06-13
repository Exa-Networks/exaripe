import re

# TODO: should list all the peers and find the ones we have no description for to report them

class Cisco (object):
	invalid_peer = ['something-unique-the-regex-will-not-match-for-peer']
	invalid_transit = ['something-unique-the-regex-will-not-match-for-transit']
	invalid_customer = ['something-unique-the-regex-will-not-match-for-customer']

	regex_ipv4 = '(\d|\d{2}|1\d{2}|2[0-4]\d|25[0-5])\.(\d|\d{2}|1\d{2}|2[0-4]\d|25[0-5])\.(\d|\d{2}|1\d{2}|2[0-4]\d|25[0-5])\.(\d|\d{2}|1\d{2}|2[0-4]\d|25[0-5])'
	# taken from http://forums.dartware.com/viewtopic.php?t=452
	regex_ipv6 = '((([0-9A-Fa-f]{1,4}:){7}(([0-9A-Fa-f]{1,4})|:))|(([0-9A-Fa-f]{1,4}:){6}(:|((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})|(:[0-9A-Fa-f]{1,4})))|(([0-9A-Fa-f]{1,4}:){5}((:((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(([0-9A-Fa-f]{1,4}:){4}(:[0-9A-Fa-f]{1,4}){0,1}((:((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(([0-9A-Fa-f]{1,4}:){3}(:[0-9A-Fa-f]{1,4}){0,2}((:((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(([0-9A-Fa-f]{1,4}:){2}(:[0-9A-Fa-f]{1,4}){0,3}((:((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(([0-9A-Fa-f]{1,4}:)(:[0-9A-Fa-f]{1,4}){0,4}((:((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(:(:[0-9A-Fa-f]{1,4}){0,5}((:((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})))(%.+)?'

	expr_hostname = re.compile('^\s*hostname\s+(?P<router>.*)\s*$')

	expr_interface = re.compile('^\s*interface\s+(.*)\s*$')
	expr_bgp_family = re.compile('^\s*address-family ipv(?P<family>4|6)\s*$')
	expr_exit = re.compile('^\s*!\s*')

	expr_ipv4 = re.compile('\s*ip\s+address\s+(?P<ip>%s)\s+(?P<netmask>%s)\s*' % (regex_ipv4,regex_ipv4))
	expr_ipv6 = re.compile('\s*ipv6\s+address\s+(?P<ip>%s)\s*/\s*(?P<netmask>12[0-8]|1[01]\d|\d{2}|\d)\s*' % regex_ipv6)

	expr_neighbor_remote_as = re.compile('\s*neighbor\s+(?P<neighbor>(?P<neighbor_v4>%s)|(?P<neighbor_v6>%s))\s+remote-as\s+(?P<asn>\d+)\s*' % (regex_ipv4,regex_ipv6))

	expr_group_remote_as = re.compile('\s*neighbor\s+(?P<peer_group>[a-zA-Z0-9\-]+)\s+remote-as\s+(?P<asn>\d+)\s*')
	expr_peer_group = re.compile('\s*neighbor\s+(?P<peer_group>%s|%s)\s+peer-group\s+(?P<name>.*)\s*' % (regex_ipv4,regex_ipv6))

	expr_any_neighbor = re.compile('\s*neighbor\s+(?P<neighbor>%s|%s)\s+.*' % (regex_ipv4,regex_ipv6))

	expr_no_neighbor_ipv4 = re.compile('\s*no\s+neighbor\s+(?P<neighbor>%s)\s+activate' % regex_ipv4)
	expr_no_neighbor_ipv6 = re.compile('\s*no\s+neighbor\s+(?P<neighbor>%s)\s+activate' % regex_ipv6)

	def __init__ (self,asn,announced_set,regex,peer=None,transit=None,customer=None):
		self.asn = asn
		self.announced_set = announced_set.upper()

		peer = peer if peer else self.invalid_peer
		transit = transit if transit else self.invalid_transit
		customer = customer if customer else self.invalid_customer

		self.expr_router_bgp = re.compile('^\s*router\s+bgp\s+%s\s*$' % self.asn)

		self.expr_peer =     re.compile('\s*neighbor\s+(?P<neighbor>(?P<neighbor_v4>%s)|(?P<neighbor_v6>%s))\s+peer-group\s+(?P<peer_group>%s)\s*' % (self.regex_ipv4,self.regex_ipv6,'|'.join(peer)))
		self.expr_transit =  re.compile('\s*neighbor\s+(?P<neighbor>(?P<neighbor_v4>%s)|(?P<neighbor_v6>%s))\s+peer-group\s+(?P<peer_group>%s)\s*' % (self.regex_ipv4,self.regex_ipv6,'|'.join(transit)))
		self.expr_customer = re.compile('\s*neighbor\s+(?P<neighbor>(?P<neighbor_v4>%s)|(?P<neighbor_v6>%s))\s+peer-group\s+(?P<peer_group>%s)\s*' % (self.regex_ipv4,self.regex_ipv6,'|'.join(customer)))

		self.expr_descr = re.compile('\s*neighbor\s+(?P<neighbor>(?P<neighbor_v4>%s)|(?P<neighbor_v6>%s))\s+description\s+%s\s*' % (self.regex_ipv4,self.regex_ipv6,regex))

		#print '\s*neighbor (?P<neighbor>%s|%s)\s+description\s+%s\s*' % (self.regex_ipv4,self.regex_ipv6,regex)

	def parse (self,stream):
		neighbors = {}
		group_asn = {}
		peer_group = {}
		v4_interface = {}
		v6_interface = {}
		v4_peer = {}
		v6_peer = {}
		peer_type = {}
		remote = {}
		descr = {}
		ignore = []
		router='no-router-name'
		in_interface = False
		in_bgp = False
		family_version = 0
		family_cast = 'unicast'

		for line in stream:
			line = line[:-1]
			# we only care about the router bgp section and interface definition
			if not in_interface and not in_bgp and not family_version:
				if self.expr_interface.search(line):
					in_interface = True
					continue
				match = self.expr_router_bgp.search(line)
				if match:
					in_bgp = True
					continue
				match = self.expr_bgp_family.search(line)
				if match:
					family_version = match.group('family')
					continue
				match = self.expr_hostname.search(line)
				if match:
					router = match.group('router')
					continue

			if in_interface:
				if self.expr_exit.search(line):
					in_interface = False
					continue
				match = self.expr_ipv4.search(line)
				if match:
					v4_interface[match.group('ip')] = match.group('netmask')
					continue
				match = self.expr_ipv6.search(line)
				if match:
					v6_interface[match.group('ip')] = match.group('netmask')
					continue
				continue
			
			if in_bgp:
				if self.expr_exit.search(line):
					in_bgp = False
					continue

				match = self.expr_any_neighbor.search(line)
				if match:
					neighbors[match.group('neighbor')] = True

				# not sure this can match anything
				match = self.expr_no_neighbor_ipv4.search(line)
				if match:
					ignore.append(match.group('neighbor'))
					continue
				# not sure this can match anything
				match = self.expr_no_neighbor_ipv6.search(line)
				if match:
					ignore.append(match.group('neighbor'))
					continue

				match = self.expr_neighbor_remote_as.search(line)
				if match:
					remote[match.group('neighbor')] = match.group('asn')
					continue
				
				# must follow expr_neighbor_remote_as for when it fails
				match = self.expr_group_remote_as.search(line)
				if match:
					group_asn[match.group('peer_group')] = match.group('asn')

				# must be before other peer group search
				match = self.expr_peer_group.search(line)
				if match:
					peer_group[match.group('peer_group')] = match.group('name')
					# do *not* insert an continue here ..

				match = self.expr_peer.search(line)
				if match:
					peer_type[match.group('neighbor')] = 'peer'
					continue

				match = self.expr_customer.search(line)
				if match:
					peer_type[match.group('neighbor')] = 'customer'
					continue

				match = self.expr_transit.search(line)
				if match:
					peer_type[match.group('neighbor')] = 'transit'
					continue

				match = self.expr_descr.search(line)
				if match:
					matched = dict([(key,str(value).replace('None','').strip()) for (key,value) in match.groupdict().iteritems()])
					name =  matched.get('peer_name','')
					mail = matched.get('peer_email','')
					announce = matched.get('peer_announced_asset','')
					macro = matched.get('peer_accepted_asset','')
					descr[matched.get('neighbor')] = macro,name,mail,announce
					continue
				continue

			if family_version:
				if self.expr_exit.search(line):
					family_version = False
					continue
				
				match = self.expr_any_neighbor.search(line)
				if match:
					neighbors[match.group('neighbor')] = True
					
				if family_version == 6:
					match = self.expr_no_neighbor_ipv6.search(line)
					if match:
						ignore.append(match.group('neighbor'))
					continue
				if family_version == 4:
					match = self.expr_no_neighbor_ipv4.search(line)
					if match:
						ignore.append(match.group('neighbor'))
						continue
					continue
				continue

		debug = True

		for dest in neighbors.keys():
			if dest in ignore:
				if debug:print 'de-activated peer', dest
				continue
			
			if dest not in descr:
				if debug: print 'missing description for', dest
				continue

			if dest not in peer_group:
				if debug: print 'no peer group for', dest
				continue

			group = peer_group[dest]
			
			if not dest in peer_type:
				if group in group_asn and group_asn[group] == self.asn:
					type = 'ibgp'
				else:
					if debug: print 'can not find type of peer connection for', dest
					continue
			else:
				type = peer_type[dest]
				
			macro,name,mail,announce = descr[dest]

			if dest in remote:
				asn = remote[dest]
			elif group in group_asn:
				asn = group_asn[group]
			else:
				if debug: print "no asn information for", dest
				continue

			# hard work to get it from the interface commiting the current work first ...
			src = 'a.b.c.d'

			if type == 'peer' and macro != '' and dest != '' and src != '':
				if announce == '': announce = self.announced_set
				export = type
			elif type == 'transit' and dest != '' and src != '' and macro == 'ANY':
				if announce == '': announce = 'ANY'
				export = type
			elif type == 'customer' and dest != '' and src != '' and macro != '':
				if announce == '': announce = 'ANY'
				export = type
			elif asn == self.asn:
				type = 'ibgp'
				export = type
			elif type == 'unknown':
				export = type
			else:
				export = 'error ' + type
				
			yield "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (router,export,group,asn,announce,src,dest,macro,mail,name)

	def nothing(self):
			match = self.expr_asn.search(line)
			if match:
				macro = macro.upper()
				announce = announce.upper()
	
				asn = match.group(1)
				if type == 'peer' and macro != '' and dest != '' and src != '':
					if announce == '': announce = self.announced_set
					export = type
				elif type == 'transit' and dest != '' and src != '' and macro == 'ANY':
					if announce == '': announce = 'ANY'
					export = type
				elif type == 'customer' and dest != '' and src != '' and macro != '':
					if announce == '': announce = 'ANY'
					export = type
				elif asn == self.asn:
					type = 'ibgp'
					export = type
				elif type == 'unknown':
					export = type
				else:
					export = 'error ' + type
	
				if router == '':
					print >> sys.stderr, 'can not extract router name'
					sys.exit(1)
	
				yield "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (router,export,group,asn,announce,src,dest,macro,mail,name)

