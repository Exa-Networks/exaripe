# XXX: Todo : handle missing AS-MACRO with "<AS-UNSPECIFIED>"

class RIPE (object):
	def __init__ (self):
		self.data = {}

	def parse (self,line):
		try:
			router,atype,group,asn,announce,src,dest,macro,mail,name = line.strip().split('|')
		except:
			print "[%s]" %line.strip()
			return False

		if src.count(':'):
			inet = 6
		else:
			inet = 4

		nasn = int(asn)
		if not self.data.has_key(nasn):
			self.data[nasn] = {}
		if not self.data[nasn].has_key(atype):
			self.data[nasn][atype] = []
		self.data[nasn][atype].append((router,atype,group,asn,announce,src,dest,macro,mail,name))

		return True

	def generate (self,display):
		result = []
		asns = self.data.keys()
		asns.sort()

		for asn in asns:
			for atype in self.data[asn]:
				if not atype in display:
					continue

				ordered = {4:{},6:{}}
				inc = 0
				for data in self.data[asn][atype]:
					router,atype,group,asn,announce,src,dest,macro,mail,name = data
					if dest.count('.'):
						a,b,c,d = dest.split('.')
						ipn = (int(a) << 24) + (int(b) << 16) + (int(c) << 8) + int(d)
						ordered[4][ipn] = data
					else:
						split = dest.split(':')
						size = len(split)
						missing = 8 - size + 1
						numeric = []
						for s in split:
							if s == '':
								for n in range(missing):
									numeric.append(0)
							else:
								# convert hexadecimal to integer
								numeric.append(int(s,16))
						
						# Handling number > 32bits is a pain, this will do for an approximation
						index = ''.join(["%05ld" % n for n in numeric])
						ordered[6][index] = data

	
				result.append("remarks:        AS%s (%s) %s" % (asn,atype,name))

				accept = []
				announce = []

				for proto in (4,6):
					keys = ordered[proto].keys()
					keys.sort()

					for ipn in keys:
						ac,an = self._generate(ordered[proto][ipn])
						accept.append(ac)
						announce.append(an)

				result += accept
				result += announce

		return result

	def _generate (self,data):
		router,atype,group,asn,announce,src,dest,macro,mail,name = data

		at = "%s at %s" % (dest.lower(),src.lower())
		if macro == 'ANY':
			macro = 'ANY and not {0.0.0.0/0}' if src.count('.') else 'ANY and not {::/0}'

		accept = "mp-import:      afi ipv4.unicast from AS%s %s accept %s" % (asn,at,macro)
		announce = "mp-export:      afi ipv4.unicast to AS%s %s announce %s" % (asn,at,announce)
	 	return accept,announce
