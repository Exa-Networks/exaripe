import re

class Juniper (object):
	invalid_peer = ['something-unique-the-regex-will-not-match-for-peer']
	invalid_transit = ['something-unique-the-regex-will-not-match-for-transit']
	invalid_customer = ['something-unique-the-regex-will-not-match-for-customer']

	expr_router = re.compile('\s+host-name (.*);')
	expr_group = re.compile('\s+(inactive:\s*)?group (.*) {')
	expr_neig = re.compile('\s+(inactive:\s*)?neighbor (.*) {')
	expr_asn = re.compile('\s+peer-as (.*);')
	expr_local = re.compile('\s+local-address (.*);')
	expr_export = re.compile('\s+export ')

	def __init__ (self,asn,announced_set,regex,peer=None,transit=None,customer=None):
		self.asn = asn
		self.announced_set = announced_set.upper()

		peer = peer if peer else self.invalid_peer
		transit = transit if transit else self.invalid_transit
		customer = customer if customer else self.invalid_customer

		self.expr_peer = re.compile('\s+export \[ *.* *('+'|'.join(peer)+') *.* *]?')
		self.expr_transit = re.compile('\s+export \[\s*.*\s*('+'|'.join(transit)+')\s*.*\s*]?')
		self.expr_customer = re.compile('\s+export \[\s*.*\s*('+'|'.join(customer)+')\s*.*\s*]?')
		
		self.expr_desc = re.compile('\s+description "%s"' % regex)

	def parse (self,stream):
		# Multiple peering with the same ASN will generate multiple lines
		skip = True
		mail = ''
		src = ''
		dest = ''
		macro = ''
		name = ''
		announce = ''
		group = ''
		type = 'unknown'
		router = ''
		inactive_group = False
		inactive_neighbor = False
	
		for line in stream:
			line = line[:-1]
			# we need to pass the group definition as we do not want to parse it
			if skip:
				if line == 'system {':
					skip = False
				if line.endswith('  bgp {'):
					skip = False
				if line == '}':
					skip = True
				continue
			
			# and as we have the test, we are leaving the logical router or the protocol section
			if line[0] == '}':
				skip = True
				continue
		
			match = self.expr_router.search(line)
			if match:
				router = match.group(1)
		
			# This may not work will all configuration
			match = self.expr_group.search(line)
			if match:
				inactive_neighbor = False
				group = match.group(2)
				if match.group(1) == None:
					inactive_group = False
				else:
					inactive_group = True
			
			if inactive_group:
				continue
			
			# set the destination IP of the BGP session
			match = self.expr_neig.search(line)
			if match:
				dest = match.group(2)
				if match.group(1) == None:
					inactive_neighbor = False
				else:
					inactive_neighbor = True
			
			if inactive_neighbor:
				continue
			
			# set the local IP of the BGP session
			match = self.expr_local.search(line)
			if match:
				src = match.group(1)
	
			# Peering or Transit
			match = self.expr_export.search(line)
			match_count = 0
			if match:
				match_peer = self.expr_peer.search(line)
				match_transit = self.expr_transit.search(line)
				match_customer = self.expr_customer.search(line)
				if match_peer:
					type = 'peer'
					match_count += 1
				if match_transit:
					type = 'transit'
					match_count += 1
				if match_customer:
					type = 'customer'
					match_count += 1
				if match_count != 1:
					type = 'unknown'
					continue
	
			# Parse the information stored in the description
			match = self.expr_desc.search(line)
			if match:
				macro = match.group('peer_accepted_asset').strip()
				name =  match.group('peer_name').strip()
				mail = match.group('peer_email').strip()
				announce = match.group('peer_announced_asset').strip()
				#print "[%s][%s][%s][%s]" % (macro,name,mail,announce)
				#print line
			else:
				#if line.find('description') > 0 :
				#	print line[:-1]
				announce = ''
	
	
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
				# do not clear src or group, it could be define for more than one peer
				dest = ''
				macro = ''
				name = ''
				announce = ''
				mail = ''
				macro = ''
				dest = ''

