import re
import sys

from network import address

# TODO: should list all the peers and find the ones we have no description for to report them

class Cisco (object):
	invalid_peer = ['something-unique-the-regex-will-not-match-for-peer']
	invalid_transit = ['something-unique-the-regex-will-not-match-for-transit']
	invalid_customer = ['something-unique-the-regex-will-not-match-for-customer']

	regex_ipv4 = '(25[0-5]|2[0-4]\d|1\d{2}|\d{2}|\d)\.(25[0-5]|2[0-4]\d|1\d{2}|\d{2}|\d)\.(25[0-5]|2[0-4]\d|1\d{2}|\d{2}|\d)\.(25[0-5]|2[0-4]\d|1\d{2}|\d{2}|\d)'
	# taken from http://forums.dartware.com/viewtopic.php?t=452
	regex_ipv6 = '((([0-9A-Fa-f]{1,4}:){7}(([0-9A-Fa-f]{1,4})|:))|(([0-9A-Fa-f]{1,4}:){6}(:|((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})|(:[0-9A-Fa-f]{1,4})))|(([0-9A-Fa-f]{1,4}:){5}((:((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(([0-9A-Fa-f]{1,4}:){4}(:[0-9A-Fa-f]{1,4}){0,1}((:((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(([0-9A-Fa-f]{1,4}:){3}(:[0-9A-Fa-f]{1,4}){0,2}((:((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(([0-9A-Fa-f]{1,4}:){2}(:[0-9A-Fa-f]{1,4}){0,3}((:((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(([0-9A-Fa-f]{1,4}:)(:[0-9A-Fa-f]{1,4}){0,4}((:((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(:(:[0-9A-Fa-f]{1,4}){0,5}((:((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})?)|((:[0-9A-Fa-f]{1,4}){1,2})))|(((25[0-5]|2[0-4]\d|[01]?\d{1,2})(\.(25[0-5]|2[0-4]\d|[01]?\d{1,2})){3})))(%.+)?'
	regex_interface = '(?P<interface>.*)\s*(?P<number>\d+(/\d+)?)'

	expr_hostname = re.compile('^\s*hostname\s+(?P<router>.*)\s*$')

	expr_interface = re.compile('^\s*interface\s+%s\s*$' % regex_interface)
	expr_bgp_family = re.compile('^\s*address-family ipv(?P<family>4|6)\s*$')

	expr_exit = re.compile('^\s*!\s*')
	expr_exit_family = re.compile('^\s*exit-address-family\s*')

	expr_ipv4 = re.compile('\s*ip\s+address\s+(?P<ip>%s)\s+(?P<netmask>%s)\s*' % (regex_ipv4,regex_ipv4))
	expr_ipv6 = re.compile('\s*ipv6\s+address\s+(?P<ip>%s)\s*/\s*(?P<netmask>12[0-8]|1[01]\d|\d{2}|\d)\s*' % regex_ipv6)

	expr_neighbor_remote_asn = re.compile('\s*neighbor\s+(?P<neighbor>(?P<neighbor_v4>%s)|(?P<neighbor_v6>%s))\s+remote-as\s+(?P<asn>\d+)\s*' % (regex_ipv4,regex_ipv6))

	expr_group_remote_asn = re.compile('\s*neighbor\s+(?P<peer_group>[a-zA-Z0-9\-]+)\s+remote-as\s+(?P<asn>\d+)\s*')
	expr_group_update_source = re.compile('\s*neighbor\s+(?P<peer_group>[a-zA-Z0-9\-]+)\s+update-source\s+%ss*' % regex_interface)

	expr_peer_group = re.compile('\s*neighbor\s+(?P<neighbor>(?P<neighbor_v4>%s)|(?P<neighbor_v6>%s))\s+peer-group\s+(?P<peer_group>.*)\s*' % (regex_ipv4,regex_ipv6))

	expr_any_neighbor = re.compile('\s*neighbor\s+(?P<neighbor>(?P<neighbor_v4>%s)|(?P<neighbor_v6>%s))\s+.*' % (regex_ipv4,regex_ipv6))

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

	def _neighbor (self,match):
		if match.group('neighbor_v4'):
			return match.group('neighbor_v4').lower()
		else:
			return address.IPv6tohex(match.group('neighbor_v6'))

	def parse (self,stream):
		neighbors = {}
		network = {}
		group_asn = {}
		group_interface = {}
		peer_group = {}
		interface_ipv4 = {}
		interface_ipv6 = {}
		interface_netmask = {}
		v4_peer = {}
		v6_peer = {}
		peer_type = {}
		remote_asn = {}
		descr = {}
		ignore = []
		router='no-router-name'
		in_interface = False
		in_bgp = False
		family_version = 0
		family_cast = 'unicast'
		last_interface = 'no-interface'

		for line in stream:
			line = line[:-1]
			# we only care about the router bgp section and interface definition
			if not in_interface and not in_bgp and not family_version:
				match = self.expr_interface.search(line)
				if match:
					last_interface = match.group('interface').lower()+match.group('number').lower()
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
					interface_ipv4[last_interface] = match.group('ip')
					interface_netmask[match.group('ip')] = match.group('netmask')
					network[address.IPv4NetworkNetmask(match.group('ip'),match.group('netmask'))] = match.group('ip')
					continue
				match = self.expr_ipv6.search(line)
				if match:
					v6 = address.IPv6tohex(match.group('ip'))
					n = int(match.group('netmask'))
					n6 = n/4
					if n6*4 != n:
						print >> sys.stderr, 'can only deal with ipv6 netmask 4bits aligned (ie: matching a letter of the IP)'
						sys.exit(1)
					interface_netmask[v6] = n
					interface_ipv6[last_interface] = v6
					network[v6[:n6]] = v6
					continue
				continue
			
			if in_bgp:
				if self.expr_exit.search(line):
					in_bgp = False
					continue

				match = self.expr_any_neighbor.search(line)
				if match:
					neighbors[self._neighbor(match)] = True

				# not sure this can match anything
				match = self.expr_no_neighbor_ipv4.search(line)
				if match:
					ignore.append(match.group('neighbor').lower())
					continue
				# not sure this can match anything
				match = self.expr_no_neighbor_ipv6.search(line)
				if match:
					ignore.append(address.IPv6tohex(match.group('neighbor')))
					continue

				match = self.expr_neighbor_remote_asn.search(line)
				if match:
					remote_asn[self._neighbor(match)] = match.group('asn')
					continue
				
				# must follow expr_neighbor_remote_asn for when it fails
				match = self.expr_group_remote_asn.search(line)
				if match:
					group_asn[match.group('peer_group')] = match.group('asn')

				match = self.expr_group_update_source.search(line)
				if match:
					group_interface[match.group('peer_group')] = match.group('interface').lower()+match.group('number').lower()

				# must be before other peer group search
				match = self.expr_peer_group.search(line)
				if match:
					peer_group[self._neighbor(match)] = match.group('peer_group')
					# do *not* insert an continue here ..

				match = self.expr_peer.search(line)
				if match:
					peer_type[self._neighbor(match)] = 'peer'
					continue

				match = self.expr_customer.search(line)
				if match:
					peer_type[self._neighbor(match)] = 'customer'
					continue

				match = self.expr_transit.search(line)
				if match:
					peer_type[self._neighbor(match)] = 'transit'
					continue

				match = self.expr_descr.search(line)
				if match:
					matched = dict([(key,str(value).replace('None','').strip()) for (key,value) in match.groupdict().iteritems()])
					name =  matched.get('peer_name','')
					mail = matched.get('peer_email','')
					announce = matched.get('peer_announced_asset','')
					macro = matched.get('peer_accepted_asset','')
					descr[self._neighbor(match)] = macro,name,mail,announce
					continue
				continue

			if family_version:
				#if self.expr_exit.search(line):
				if self.expr_exit_family.search(line):
					family_version = False
					continue
				
				match = self.expr_any_neighbor.search(line)
				if match:
					neighbors[self._neighbor(match)] = True
					
				if family_version == 6:
					match = self.expr_no_neighbor_ipv6.search(line)
					if match:
						ignore.append(address.IPv6tohex(match.group('neighbor')))
					continue
				if family_version == 4:
					match = self.expr_no_neighbor_ipv4.search(line)
					if match:
						ignore.append(match.group('neighbor').lower())
						continue
					continue
				continue

		if router == '':
			print >> sys.stderr, 'can not extract router name'
			sys.exit(1)

		for dest in neighbors.keys():
			if dest in ignore:
				#print >> sys.stderr, 'de-activated peer', dest
				continue
			
			if dest not in descr:
				print >> sys.stderr, 'missing description for', dest
				continue

			if dest not in peer_group:
				print >> sys.stderr, 'no peer group for', dest
				continue

			group = peer_group[dest]
			
			if not dest in peer_type:
				if group in group_asn and group_asn[group] == self.asn:
					type = 'ibgp'
				else:
					print >> sys.stderr, 'can not find type of peer connection for', dest
					continue
			else:
				type = peer_type[dest]
				
			macro,name,mail,announce = descr[dest]

			if dest in remote_asn:
				asn = remote_asn[dest]
			elif group in group_asn:
				asn = group_asn[group]
			else:
				print >> sys.stderr, 'no asn information for', dest
				continue

			try:
				if address.isIPv4(dest):
					src = interface_ipv4[group_interface[peer_group[dest]]]
				else:
					src = interface_ipv6[group_interface[peer_group[dest]]]
			except KeyError:
				# hard work to get it from the interface commiting the current work first ...
				if address.isIPv4(dest):
					src = '0.0.0.0'
					for r in range(32,0,-1):
						m = address.IPv4bitsToNetmask(r)
						n = address.IPv4NetworkNetmask(dest,m)
						if network.has_key(n):
							src = network[n]
							continue
				else:
					src = '::'
					d = address.IPv6tohex(dest)
					for r in range(0,28):
						k = d[:r]
						if network.has_key(k):
							src = address.hextoIPv6(network[k])
							dest = address.hextoIPv6(dest)
							break

			if type == 'customer' and macro != '' and dest != '' and src != '':
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
