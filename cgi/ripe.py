#!/usr/bin/env python

debug = True
store = "/images"
allocation = "195.66.224.0/19"

import sys
import os
import cgi
import re

if debug:
	import cgitb
	cgitb.enable()

def home (allocation):
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
		<input type="text" name="allocation" size="30" value="%s" />
		<input type="submit" value="Submit" />
		<br />
		Rendering :
		<input type="radio" name="rendering" value="svg" checked="checked" />svg
		<input type="radio" name="rendering" value="png"                   />png
		<br />
		Experimental :
                <input type="checkbox" name="javascript" value="true" checked="checked" />javascript event (untick for testing)
	</form>
	<br/>
	Find the original perl version on which this work is based at: <a href="http://crazygreek.co.uk/content/ripe">http://crazygreek.co.uk/content/ripe</a>
	<br/>
	<br/>
	<b> Disclaimer about the SVG rendering </b>
	<ul>
		<li/>it is CPU intensive. rendering a full /14 on a netbook will be slow :D
		<li/>it is working on Safari/Webkit (and even then the rendering is not perfect)
		<li/>Firefox renders the image and javascript but is not able to handle the non-javascript svg events
		<li/>IE is its usual self .... ie: useless :D
		<li/>Other browsers not tested
	</ul>
</body>""" % allocation
	sys.exit(0)

def validate_allocation (allocation):
	match = re.compile('(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/([0-9]{1,2})').match(allocation)
	if not match:
		return False
	for i in range(1,5):
		if int(match.group(i)) > 255:
			return False
	if int(match.group(5)) > 32:
		return False
	return True

def validate_rendering (rendering):
	return rendering in ['svg','png']

def validate_boolean (boolean):
	return boolean in ['true','false']

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
	home(allocation)

form = cgi.FieldStorage()

if not form.has_key('allocation'):
	home(allocation)

allocation = form.getfirst('allocation')
if not validate_allocation(allocation):
	home(allocation)

if not form.has_key('rendering'):
	home(allocation)

rendering = form.getfirst('rendering')
if not validate_rendering(rendering):
	home(allocation)

javascript = form.getfirst('javascript')
if not validate_boolean(javascript):
	javascript = 'false'

xslt   = os.path.join(dir,'etc','render','allocation-%s.xsl' % rendering)
img    = "%s.%s" % (allocation.replace('/','-'),rendering)

from render.ripe import Whois
try:
	whois = Whois(allocation)
except ValueError,e:
	print str(e)
	home(allocation)

if rendering == 'svg':
	from render.svg import SVG as Image
	image = Image(allocation,store,75,75,105,20,4,True if javascript == 'true' else False)
if rendering == 'png':
	from render.png import PNG as Image
	image = Image(allocation,store,75,75,105,20,4)

from render.html import HTML
html = HTML(xslt,image)

try:
	image.generate(whois.rpsl,cache,img)
	html.generate(whois.rpsl,sys.stdout)
except IOError,e:
	print '%s' % str(e)
sys.exit(0)

