#!/usr/bin/env python

import os
import sys

from optparse import OptionParser

class CommandError (Exception): pass

class CommandLine (dict):
	options = {
		'verbose':	('verbose','v','store_true','verbose'),

		'asn':		('asn','a','store','the asn of your network'),
		'macro':	('macro','s','store','the AS-MACRO (AS-SET) used when exporting to peers'),

		# for source/juniper - locate-juniper
		'folder':	('folder','f','store_true','where to look for the configuration files'),
		'dump':		('dump','d','store_true','the not print the file name, print the content'),

		# for parser/juniper - parser-juniper
		'description-regex':	('description-regex','d','store','the regex to extract information from the juniper peer description example: (?P<peer-accepted-asset>.*?)\|(?P<peer-name>.*?)\|(?P<peer-email>[^|]*)\|?(?P<peer-announced-asset>.*)'),
		'policy-peer':		('peer','p','append','the policy used in the router configuration for peers'),
		'policy-transit':	('transit','t','append','the policy used in the router configuration for transit'),
		'policy-customer':	('customer','c','append','the policy used in the router configuration for customers'),
		'policy-multicast':	('multicast','m','append','the policiy used in the router configuration for multicast'),

		# for export/ripe - export-ripe
		'export':	('export','e','append','what type of connection should be exported (peer,transit,customer)'),

		'filter':	('filter','f','store_true',''),
		'aligned':	('aligned','a','store_true','does the ip have to be aligned with their netmask'),
		'exchange':	('exchange','x','append','the exchange affected by the maintenance'),
		'router':	('router','r','append','the router affected by the maintenance'),
	}

	def __init__ (self,usage,options):
		dict.__init__(self)

		self._usage = usage % os.path.basename(sys.argv[0])
		parser = OptionParser(self._usage)

		for option in options:
			if option in self.options:
				long,short,action,help = self.options[option]
				parser.add_option('-%s' % short, '--%s' % long, dest=option, action=action, help=help)
			else:
				raise CommandError('you have a typo with your option name in your code')

		(opts, args) = parser.parse_args()

		for key in options:
			try:
				long,short,action,help = self.options[key]
				self[key] = getattr(opts,key)
			except AttributeError:
				pass

		if args:
			self['cmdline'] = args
		else:
			self['cmdline'] = []

	def usage (self,problem):
		print >> sys.stderr , self._usage
        	print >> sys.stderr , problem
        	sys.exit(1)     

if __name__ == '__main__':
	usage = """\
%s [-h] [-d] [folder]
A test program to verify that the command line library is working correctly."""
	options = ['dump']
	cmd = CommandLine(usage,options)
	for option in options:
		print "%-15s\t%s" % (option,str(cmd[option]))
