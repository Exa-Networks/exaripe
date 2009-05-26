#!/usr/bin/env python

# XXX: Todo : handle missing AS-MACRO with "<AS-UNSPECIFIED>"

import time
import os
import sys

from network.option.cmd import CommandLine
from network.option.ripe import RIPE as OptionsRIPE
from network.export.ripe import RIPE as ExportRIPE

usage = """ %s [-h] [header] [footer]
parse a | separated reprentation of a router configuration and generate a RIPE asnum."""

cmd = CommandLine(usage,[])

options = OptionsRIPE()

header = options['header']
footer = options['footer']

display_options = ['transit','peer','customer']

exporter = ExportRIPE()

for line in sys.stdin.readlines():
	if not exporter.parse(line):
		print "problem parsing line:\n" + line.strip()
		sys.exit(1)
		
body = exporter.generate(display_options)
replace = {'generated':time.strftime("%Y%m%d %H:%M:%S")}

print header % replace,
print '\n'.join(body)
print footer % replace,

sys.exit(0)

