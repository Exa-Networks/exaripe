#!/usr/bin/env python

import sys

from network.option.cmd import CommandLine
from network.option.juniper import Juniper as OptionsJuniper
from network.option.ripe import RIPE as OptionsRIPE

from network.parse.juniper import Juniper as ParserJuniper

usage = """%s [-a asn] [-m as-macro] [-p peer] [-t transit] [-c customer]

parse one or more juniper configuration provided on stdin
and generate an easily parseable list of all bgp session
"""

cmd = CommandLine(usage,['asn','macro','description-regex','policy-peer','policy-transit','policy-customer','policy-multicast'])

option_ripe = OptionsRIPE()
option_juniper = OptionsJuniper()

cmd_asn = cmd['asn']
cmd_regex = cmd['description-regex']
cmd_macro = cmd['macro']
cmd_peer = cmd['policy-peer'] 
cmd_customer = cmd['policy-customer']
cmd_transit = cmd['policy-transit']
cmd_multicast = cmd['policy-multicast']

asn = option_ripe['asn'] if cmd_asn is None else cmd_asn
try:
	if asn[:2] == 'AS':
		asn = asn[:2]
	asn = str(int(asn))
except:
	print >> sys.stderr, 'invalid ASN'
	sys.exit(1)

macro = option_ripe['macro'] if cmd_macro is None else cmd_macro
regex = option_juniper['regex'] if cmd_regex is None else cmd_regex
peer = option_juniper['peer'].split(' ') if cmd_peer is None else cmd_peer
customer = option_juniper['customer'].split(' ') if cmd_customer is None else cmd_customer
transit = option_juniper['transit'].split(' ') if cmd_transit is None else cmd_transit
multicast = option_juniper['multicast'].split(' ') if cmd_multicast is None else cmd_multicast

if peer == [] and customer == [] and transit == []:
	print >> sys.stderr, 'you need to specify at least on of the option -p,-t,-c with a parameter'
	sys.exit(1)

parser = ParserJuniper (asn,macro,regex,peer,transit,customer,multicast)

found = False
for r in parser.parse(sys.stdin):
	found = True
	print r
	
if not found:
	print >> sys.stderr, 'could not find a single bgp relation'
	sys.exit(1)
