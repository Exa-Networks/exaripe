#!/usr/bin/env python

from __future__ import with_statement

import time
import os
import sys

from network.option.cmd import CommandLine
from network.option.notification import Template as OptionsTemplate
from network.option.notification import Reason as OptionsReason
from network.export.notification import Notification as ExportNotification

usage = """ %s [-h] 
XXX: does something."""

cmd = CommandLine(usage,[])

templates = OptionsTemplate()
reasons = OptionsReason()

exporter = ExportNotification()

for line in sys.stdin.readlines():
	if not exporter.parse(line):
		print >> sys.stderr, "problem parsing line:\n" + line.strip()
		sys.exit(1)

routers = [exporter.routers()[0]]
atypes = ['peer']
groups = []

def showoption (prefix,options):
	print '\r',prefix
	store = {}
	index = 0
	for k in options.keys():
		store[str(index)] = k
		index += 1
	keys = store.keys()
	keys.sort()
	
	with open('/dev/tty','r') as stdin:
		while True:
			for k in keys:
				print k, store[k].replace('_',' ')
			print '\rEnter your selection : ',
			s = stdin.readline().strip()
			if s in keys: break
	
	return options[store[s]]
	
def template ():
	return showoption('template...',templates)
	
def reason ():
	return showoption('template...',reasons)

def get_time (prefix):
	import re

	re_date = re.compile('(20[01]\d)/(0?\d|1[012])/(0?\d|1\d|2\d|3[01]) (0?\d|1\d|2[0123]):(0?\d|[12345]\d)')

	print '\r', prefix
	with open('/dev/tty','r') as stdin:
		while True:
			print "\rdate YYYY/MM/DD HH:MM ",
			d = stdin.readline().strip()
			if re_date.match(d): break
		
		mt = time.mktime(time.strptime("%s:00" % d,"%Y/%m/%d %H:%M:%S"))
		gmt = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(mt))
		local = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mt))
		
		if time.tzname[0]:
			return "%s %s (%s GMT)" % (local,time.tzname[1],gmt)
		return "%s GMT" % gmt

for email, body in exporter.filter_router(routers).filter_type(atypes).filter_group(groups).generate(template,reason,get_time):
	if email:
		print "email is : %s" % email
		print body
		print
		print

#print body

sys.exit(0)

