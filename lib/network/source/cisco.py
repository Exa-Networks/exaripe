#!/usr/bin/env python

from __future__ import with_statement

import os
import re

# XXX: NO ERROR HANDLING OF PROBLEM OPENING FILES

class CiscoFile (list):
	def __init__ (self,directory):
		list.__init__(self)
		
		expr_file = re.compile('([^\.].*[^~])')
		last = {}
		router = 0
	
		for files in os.walk(directory):
			directory = files[0]
			for file in files[2]:
				match = expr_file.match(file)
				if match:
					last[router] = (directory,file)
					router += 1
#					router = match.group(1)
#					date = int(match.group(2))
#					time = int(match.group(3))
#					if last.has_key(router):
#						newest_date = last[router][0]
#						if date < newest_date:
#							continue
#						elif date == newest_date:
#							if time < last[router][1]: continue
#					last[router] = (date,time,directory,file)
	
		routers = last.keys()
		if len(routers) == 0:
			return []
	
		for router in routers:
			directory,file = last[router]
			self.append(os.path.join(directory,file))

class CiscoConfiguration (list):
	def __init__ (self,directory):
		list.__init__(self)

		names = CiscoFile(directory)

		for name in names:
			with open(name) as f:
				self.append(''.join(f.readlines()))

if __name__ == '__main__':
	import sys
	from ripe.option.cmd import CommandLine, CommandLineError

	usage = 'usage: %s folder' % sys.argv[0]
	try:
		cmd = CommandLine(usage,['dump'])
	except CommandLineErrror:
		print >> sys.stderr, usage
		sys.exit(1)	

	try:
		directory = cmd['cmdline'][0]
	except KeyError:
		print >> sys.stderr, usage
		sys.exit(1)	

	if cmd['dump']:
		confs = CiscoConfiguration(directory)
	else:
		confs = CiscoFile(directory)

	if confs == []:
		print >> sys.stderr, 'could not find any junos configuration'
		sys.exit(1)
	
	for conf in confs:
		print conf
	sys.exit(0)

