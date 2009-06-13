#!/usr/bin/env python

import sys

from network.option.cmd import CommandLine
from network.option.cisco import Cisco as OptionsCisco
from network.option.ripe import RIPE as OptionsRIPE

from network.parse.cisco import Cisco as ParserCisco

usage = """%s [-a asn] [-m as-macro] [-p peer] [-t transit] [-c customer]

parse one or more juniper configuration provided on stdin
and generate an easily parseable list of all bgp session
"""

cmd = CommandLine(usage,['asn','macro','description-regex','policy-peer','policy-transit','policy-customer'])

option_ripe = OptionsRIPE()
option_cisco = OptionsCisco()

cmd_asn = cmd['asn']
cmd_regex = cmd['description-regex']
cmd_macro = cmd['macro']
cmd_peer = cmd['policy-peer'] 
cmd_customer = cmd['policy-customer']
cmd_transit = cmd['policy-transit']

asn = option_ripe['asn'] if cmd_asn is None else cmd_asn
try:
	if asn[:2] == 'AS':
		asn = asn[:2]
	asn = str(int(asn))
except:
	usage('invalid ASN')

macro = option_ripe['macro'] if cmd_macro is None else cmd_macro
regex = option_cisco['regex'] if cmd_regex is None else cmd_regex
peer = option_cisco['peer'].split(' ') if cmd_peer is None else cmd_peer
customer = option_cisco['customer'].split(' ') if cmd_customer is None else cmd_customer
transit =  option_cisco['transit'].split(' ') if cmd_transit is None else cmd_transit

if peer == [] and customer == [] and transit == []:
	usage('you need to specify at least on of the option -p,-t,-c with a parameter')

parser = ParserCisco (asn,macro,regex,peer,transit,customer)

found = False
for r in parser.parse(sys.stdin):
	found = True
	print r
	
if not found:
	usage('could not find a single bgp relation')
