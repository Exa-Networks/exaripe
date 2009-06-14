#!/usr/bin/env python

from network.option.cmd import CommandLine
from network.option.cisco import Cisco as Options
from network.source.cisco import CiscoFile, CiscoConfiguration

usage = """%s [-h] [-d] [folder]

search the folder specified (or the one configured) for cisco configuration backup
(most likely used with the Cisco ftp configuration export on commit)
and return the most recent configuration for each router based on its filename.
"""

cmd = CommandLine(usage,['dump'])

try:
	directory = cmd['cmdline'][0]
except IndexError:
	options = Options()
	directory = options['backup']

if cmd['dump']:
	confs = CiscoConfiguration(directory)
else:
	confs = CiscoFile(directory)

if confs == []:
	print >> sys.stderr, 'could not find any junos configuration'
	sys.exit(1)

for conf in confs:
	print conf
