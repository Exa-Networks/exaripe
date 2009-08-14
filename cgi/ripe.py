#!/usr/bin/env python

debug = True
svg = False
store = "/images"

rendering = 'svg' if svg else 'image'
ext = 'svg' if svg else 'png'

import sys
import os
import cgi

if debug:
	import cgitb
	cgitb.enable()

def home ():
	print """\
<html>
<head>
	<title>See a RIPE allocation</title>
</head>
<body>
	<h1><center>RIPE allocation display</center></h1>
	<br/>
	<br/>
	<form name="range" action="ripe" method="get">
		Range : 
		<input type="text" name="allocation" size="30" value="195.66.224.0/19" />
	</form>
	<br/>
	find the original perl version at: <a href="http://crazygreek.co.uk/content/ripe">http://crazygreek.co.uk/content/ripe</a>
</body>"""
	sys.exit(0)

def validate (allocation):
	import re
	match = re.compile('(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/([0-9]{1,2})').match(allocation)
	if not match:
		return False
	for i in range(1,5):
		if int(match.group(i)) > 255:
			return False
	if int(match.group(5)) > 32:
		return False
	return True

program = os.path.abspath(sys.argv[0])
dir = os.path.abspath(os.path.join(os.path.dirname(program),'..'))
cache = os.path.join(dir,'cache')
lib  = os.path.join(dir,'lib')

sys.path += [lib]

print "Content-Type:text/html"
print ""

if not os.path.exists(cache):
	print "destination folder does not exists"
	if debug: print cache
	home()

form = cgi.FieldStorage()

if not form.has_key('allocation'):
	home()

allocation = form.getfirst('allocation')
if not validate(allocation):
	home()

xslt   = os.path.join(dir,'etc','render','allocation-%s.xsl' % rendering)
img    = "%s.%s" % (allocation.replace('/','-'),ext)

from render.ripe import Whois
try:
	whois = Whois(allocation)
except ValueError,e:
	print str(e)
	home()

if svg:	from render.svg import SVG as Map
else:	from render.image import Image as Map
map = Map(allocation,store,75,75,105,20,4)

from render.html import HTML
html = HTML(xslt,map)

try:
	map.generate(whois.rpsl,cache,img)
	html.generate(whois.rpsl,sys.stdout)
except IOError,e:
	print '%s' % str(e)
sys.exit(0)

