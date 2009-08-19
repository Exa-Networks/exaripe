#!/usr/bin/env python

import os
from network.option.options import Options

class Template (Options):
	folder = os.path.join('notification','template')
	format = {
	}

class Reason (Options):
	folder = os.path.join('notification','reason')
	format = {
	}

if __name__ == '__main__':
	import sys

	def usage (problem):
		print >> sys.stderr , 'usage: %s [files]' % sys.argv[0]
		print >> sys.stderr , problem
		sys.exit(1)

	for options in [NotificationTemplate(),NotificationReason()]:
		for key in options.valid:
			if key not in options:
				usage('no configuration file found')

		for option in options:
			if options.format[option]:
				print option,'\t','\n...\t'.join(options[option].split('\n'))
			else:
				print "%-15s\t%s" % (option,options[option])
	sys.exit(0)
