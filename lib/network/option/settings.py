#!/usr/bin/env python

import os
from network.option.options import Options

class Settings (Options):
	folder = '.'
	format = {
		'smtp' :		False,
		'production' :	False,
	}

if __name__ == '__main__':
	import sys

	def usage (problem):
		print >> sys.stderr , 'usage: %s [files]' % sys.argv[0]
		print >> sys.stderr , problem
		sys.exit(1)

	options = Settings()

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
