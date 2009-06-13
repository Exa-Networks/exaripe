#!/usr/bin/env python

from network.option.options import Options

class Cisco (Options):
	folder = 'cisco'
	format = {
		'backup' :		False,
		'export' :		False,
		'int_description' :	False,
		'bgp_description' :	False,
		'customer' :		False,
		'peer' :		False,
		'transit' :		False,
	}

if __name__ == '__main__':
	import sys

	def usage (problem):
		print >> sys.stderr , 'usage: %s [files]' % sys.argv[0]
		print >> sys.stderr , problem
		sys.exit(1)

	options = Juniper()

	keys = ['asn','cisco','company','customer','export','footer','header','juniper','macro','peer','preference','secret','transit']
	for key in options.valid:
		if key not in options:
			usage('no configuration file found')


	for option in options:
		if options.format[option]:
			print option,'\t','\n...\t'.join(options[option].split('\n'))
		else:
			print "%-15s\t%s" % (option,options[option])
	sys.exit(0)
