#!/usr/bin/env python

from __future__ import with_statement

import sys
import os
from twisted.python import usage

class Options(usage.Options):
	def __init__ (self):
		usage.Options.__init__(self)
	
	optFlags = [
		["png",   "p", "generate png"],
		["html",  "h", "generate html"],
		["debug", "d", "turn debugging on"],
	]
	optParameters = [
		["location",   "l", "/var/www",      "Where the result should be writen"],
		["allocation", "a", "82.219.0.0/16", "Your RIPE allocation"],
		["left",       "l", 105,             "Padding Left",         int],
		["right",      "r",  50,             "Padding Right",        int],
		["top",        "t",  75,             "Padding Top",          int],
	]

option = Options()
try:
    option.parseOptions()
except usage.UsageError, errortext:
    print '%s: %s' % (sys.argv[0], errortext)
    print '%s: Try --help for usage details.' % (sys.argv[0])
    sys.exit(1)


location = option['location']
xslt = os.path.join(os.environ.get('ETC','/etc'),'render','allocation.xsl')
javascript = os.path.join(os.environ.get('ETC','/etc'),'render','allocation.js')

if not os.path.exists(location):
	print >> sys.stderr, "destination folder does not exists"
	sys.exit(1)

if not os.path.isdir(location):
	print >> sys.stderr, "destination is not a directory"
	sys.exit(1)

from render.ripe import Whois
whois = Whois(option['allocation'])

print >> sys.stderr, "copying javascript"
with open(javascript) as r:
	with open(os.path.join(location,'allocation.js'),'w+') as w:
		content = r.read()
		w.write(content)

print >> sys.stderr, "generating png"
from render.image import Image
image = Image(option['allocation'],
		option['top'],option['left'],option['right'],
		6,20,4)
image.generate(whois.rpsl,location,'image.png')

print >> sys.stderr, "generating html"
from render.html import HTML
html = HTML(xslt,image)
html.generate(whois.rpsl,location,'index.html')

sys.exit(0)

