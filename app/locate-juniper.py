#!/usr/bin/env python

from network.option.cmd import CommandLine
from network.option.juniper import Juniper as Options
from network.source.juniper import JuniperFile, JuniperConfiguration

usage = """%s [-h] [-d] [folder]

search the folder specified (or the one configured) for juniper configuration backup
(most likely used with the Juniper ftp configuration export on commit)
and return the most recent configuration for each router based on its filename.
"""

cmd = CommandLine(usage,['dump'])

try:
	directory = cmd['cmdline'][0]
except IndexError:
	options = Options()
	directory = options['backup']

if cmd['dump']:
	confs = JuniperConfiguration(directory)
else:
	confs = JuniperFile(directory)

if confs == []:
	print >> sys.stderr, 'could not find any junos configuration'
	sys.exit(1)

for conf in confs:
	print conf
