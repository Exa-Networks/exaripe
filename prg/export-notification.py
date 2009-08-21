#!/usr/bin/env python

from __future__ import with_statement

import time
import os
import sys
import cgi
import re

from network.option.cmd import CommandLine
from network.option.notification import Notification as OptionsNotification
from network.export.notification import Notification as ExportNotification



usage = """ %s [-h] 
XXX: does something."""

cmd = CommandLine(usage,[])

exporter = ExportNotification()

for line in sys.stdin.readlines():
	if not exporter.parse(line):
		print >> sys.stderr, "problem parsing line:\n" + line.strip()
		sys.exit(1)

routers = [exporter.routers()[0]]
atypes = ['peer']
groups = []

exporter.filter_router(routers)
exporter.filter_type(atypes)
exporter.filter_group(groups)

###############################################
# This should be in its own include file ..
###############################################

def raw (prefix,valid):
	while True:
		with open('/dev/tty','r') as stdin:
			print >> sys.stderr, '\r', prefix,
			answer = stdin.readline().strip()
			if answer in valid: break
	return answer

class Template (object):
	re_date = re.compile('(20[01]\d)/(0?\d|1[012])/(0?\d|1\d|2\d|3[01]) (0?\d|1\d|2[0123]):(0?\d|[12345]\d)|(now)|(now)\+(\d+)([HhMm])')
	re_include = re.compile('^\s?<include\s+(.*)\s?>\s?$')
	re_ask = re.compile('<ask\s+(?P<name>.*)\s+(?P<type>.*)\s?>')

	def function_date_time (self,prefix):
		print >> sys.stderr, '\r', prefix.replace('_',' ')
		with open('/dev/tty','r') as stdin:
			while True:
				print >> sys.stderr, "\rdate YYYY/MM/DD HH:MM ",
				answer = stdin.readline().strip()
				if self.re_date.match(answer): break

			if answer.startswith('now'):
				add = 0
				if answer[-1] in ['H','h']: add = 60*60
				if answer[-1] in ['M','m']: add = 60
				if add: add *= int(answer[4:-1])
				print 'add is ', add
				mt = time.mktime(time.localtime(time.time()+add))
			else:
				mt = time.mktime(time.strptime("%s:00" % d,"%Y/%m/%d %H:%M:%S"))
			print "mt is", mt
			gmt = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(mt))
			local = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mt))

			if time.tzname[0]:
				return "%s %s (%s GMT)" % (local,time.tzname[1],gmt)
			return "%s GMT" % gmt

	function = {
		'date_time' : function_date_time,
	}

	def __init__ (self,section='template'):
		reply = []
		fname,content = self.query('%s :' % section,OptionsNotification(section))
		for line in content.split('\n'):
			match = self.re_include.search(line)
			if match:
				reply.append(Template(match.group(1)).message())
				continue
			match = self.re_ask.search(line)
			if match and match.group(2) in self.function.keys():
				reply.append(line.replace(match.group(0),self.function[match.group(2)](self,match.group(1))))
				continue
			reply.append(line)
			
		self._message = '\n'.join(reply)
		self._subject = fname.replace('_',' ')

	def query (self,prefix,options):
		print >> sys.stderr, '\r',prefix
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
					print >> sys.stderr, '\r',k, store[k].replace('_',' ')
				print >> sys.stderr, '\rEnter your selection : ',
				s = stdin.readline().strip()
				if s in keys: break
	
		return store[s],options[store[s]]
	
	def message (self):
		return self._message
	
	def subject (self):
		return self._subject

###############################################

mails = []
missing = []

for sender,recipient,subject,body,asn,organisation in exporter.generate(Template()):
	if not recipient:
		if organisation:
			missing.append(organisation)
			continue
		missing.append(asn)
		continue
	mails.append("""\
<mail sender="%s" recipient="%s" subject="%s">
%s
</mail>
""" % (
	cgi.escape(sender),
	cgi.escape(recipient),
	cgi.escape(subject),
	cgi.escape(body),
))

print >> sys.stderr, '-'*30, 'PREVIEW (%-3d recipients)' % len(mails), '-'*30
print >> sys.stderr, """%s""" % mails[0],
print >> sys.stderr, '-'*80
print >> sys.stderr

print >> sys.stderr, '\rThose organisations have no contact information\n%s\n[Y/N]' % "\n * ".join(missing)

#print """<xml>%s</xml>""" % "".join(mails)


sys.exit(0)

