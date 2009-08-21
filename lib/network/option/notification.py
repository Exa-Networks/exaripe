#!/usr/bin/env python

import os
from network.option.options import Options

class Notification (Options):
	format = {
	}
	def __init__ (self,section):
		self.folder = os.path.join('notification',section)
		Options.__init__(self)

if __name__ == '__main__':
	import sys

	def usage (problem):
		print >> sys.stderr , 'usage: %s [files]' % sys.argv[0]
		print >> sys.stderr , problem
		sys.exit(1)

	options = Notification('template')
	for key in options.valid:
		if key not in options:
			usage('no configuration file found')

	for option in options:
		if options.format[option]:
			print option,'\t','\n...\t'.join(options[option].split('\n'))
		else:
			print "%-15s\t%s" % (option,options[option])
	sys.exit(0)
