import os
import cgi

from netaddr import CIDR,nrange

class SVG (object):
	def __init__ (self,allocation,prefix,top,left,right,size_y,size_x,js=False):
		self.tooltip_id = 0
		self.allocation = allocation
		self.prefix = prefix
		self.left = left
		self.right = right
		self.top = top
		self.js = js

		self.font = max(1,int(2*size_y/3)) 
		self.size_y = size_y
		self.size_x = size_x
		self.length = size_x*256

		self.location = {}

		self.name = ''
		self.width = 0
		self.height = 0

	def _svg (self,sx,sy):
		return """\
<?xml version="1.0" encoding="UTF-8"?>
<svg width="%d" height="%d" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve">
%%s
</svg>
""" % (sx,sy)
#viewBox="0 0 130 200" 

	def _line (self,x1,y1,x2,y2,color,stroke=False):
		return """\
<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="rgb%s" stroke-width="1"%s/>
""" % (str(x1),str(y1),str(x2),str(y2),str(color),' stroke-dasharray="3,2"' if stroke else '')

#<rect x="%d" y="%d" width="%d" height="%d" style="fill:rgb%s;stroke-width:1;stroke:rgb%s"/>
	def _rectangle (self,x,y,sx,sy,color_border=(0,0,0),color_fill=(255,255,255),javascript=None):
		return"""\
<rect x="%s" y="%s" width="%s" height="%s" fill="rgb%s" stroke-width="1" stroke="rgb%s" %s/>
""" % (str(x),str(y),str(sx),str(sy),str(color_fill),str(color_border),javascript if javascript else '')

	def _text (self,x,y,font,color,string,options=None):
		return """\
<text x="%s" y="%s" fill="rgb%s" font-size="%s" %s>
%s
</text>
""" % (str(x),str(y),str(color),str(font),options if options else '',cgi.escape(string))

	def _tooltip (self,x,y,font,color,string,tooltips,options=None):
		yn = y+self.size_y
		d = {
			'id': 'tooltip%d' % self.tooltip_id,
			'x' : str(x+2),
			'y' : str(y),
			'x-box' : str(x-2),
			'y-box' : str(yn),
			'color' : str(color),
			'font' : str(font),
			'string' : cgi.escape(string),
			'options' : options if options else '',
			'rgb' : '(155,155,155)',
			'width' : max([len(s) for s in tooltips])*self.font/2 + 10,
			'height' : len(tooltips)*font+5,
		}
		self.tooltip_id += 1

		tooltip = ""
		for t in tooltips:
			d['tooltip'] = cgi.escape(t)
			yn += font
			d['y-next'] = str(yn)
			tooltip += """\
  <text x="%(x)s" y="%(y-next)s" font-size="%(font)s" fill="black" visibility="hidden">%(tooltip)s
    <set attributeName="visibility" from="hidden" to="visible" begin="%(id)s.mouseover" end="%(id)s.mouseout"/>
  </text>
""" % d
		d['tooltip'] = tooltip
		return """\
<text id="%(id)s" x="%(x)s" y="%(y)s" fill="rgb%(color)s" font-size="%(font)s" %(options)s>
%(string)s
</text>""" % d, \
"""\
   <rect x="%(x-box)s" y="%(y-box)s" width="%(width)s" height="%(height)s" visibility="hidden" style="fill:rgb(255,255,255);fill-opacity:1.0;stroke:blue;stroke-width:2;">
       <set attributeName="visibility" from="hidden" to="visible" begin="%(id)s.mouseover" end="%(id)s.mouseout"/>
   </rect>
%(tooltip)s
""" % d

	def generate (self,rpsl,dir,name):
		cidr = CIDR(self.allocation)

		self.name = os.path.join(dir,name)
		self.link = os.path.join(self.prefix,name)
		left = (self.font*len(cidr[-1])/5) + 10
		self.width = left + 256*self.size_x + 10
		self.height = (rpsl.nb24s*self.size_y) + self.top + 1 + 100

		per24 = rpsl.fragment()

		slash = {}
		for s in xrange(18,32+1):
			slash[pow(2,32-s)] = s

		color = {
			'white' : (255, 255, 255),
			'grey'	: (100, 100, 100),
			'black' : (  0,   0,   0),
			'blue'  : (  0,   0, 255),
			'red'   : (255,   0,   0),
			'green' : (0,   255,   0),
		}
		
		background = {
			32      : (230, 230,   0),
			31      : (150, 250,   0),
			30      : (  0, 155,   0),
			29      : (  0, 155,  50),
			28      : (  0, 200, 100),
			27      : (  0, 255, 150),
			26      : (  0, 255, 200),
			25      : (  0, 250, 250),
			24      : (  0, 200, 255),
			23      : (150, 150, 200),
			22      : (250, 200, 170),
			21      : (255, 250,   0),
			20      : (250, 100, 150),
			19      : (255, 125,   0),
			18      : (200, 100, 100),
		}
		
		svg = self._svg(left + self.size_x*256 + 10, (rpsl.nb24s*self.size_y) + self.top + 10)
		content = ''
		tooltips = ''

		if self.js:
			content += '''
<script type="text/javascript"><![CDATA[
function showPrefix(id) {
  elt = top.document.getElementById(id);
  var loc = top.document.getElementById("loc");
  loc.innerHTML = elt.innerHTML;
  loc.style.display = "block";
}

function hidePrefix() {
  top.document.getElementById("loc").innerHTML = "";
  var loc = top.document.getElementById("loc");
  loc.style.display = "none";
}

function showPrefixAlert(id) {
  elt = top.document.getElementById(id);
  if (elt == undefined)
    return;
  var txt = "";
  kids = elt.childNodes;
  for (var i = 0; kids.length - i; i++) {
    if (kids[i].innerHTML != "") {
      txt += kids[i].innerHTML;
      txt += "\\n";
    }
  }
  alert(txt);
}
]]></script>
'''

		# The outer box
		content += self._rectangle(left,self.top, self.length,rpsl.nb24s*self.size_y, color['black'],color['white'])

		# The color legend
		keys = background.keys()
		keys.sort()
		x = 1
		for k in keys:
			p = str(int(x*100/(len(keys)+2))) + "%"
			content += self._rectangle(p,5, 12,12, color['black'],background[k])
			content += self._text(p,30,self.font,color['black'],'/%d' % k)
			x += 1
		
		# The horizontal lines
		y = self.top
		ranges = []
		for n in nrange(cidr[0],cidr[-1],256):
			ranges.append((n,y))
			range = str(n)
			t = y + self.font + 1
			content += self._line(left,y, left+self.length,y, color['black'], False)
			content += self._text(left - (self.font*len(range)/2), t, self.font,color['black'],range)
			y+=self.size_y
		
		# The horizontal numbering
		yt = self.top - 12
		yb = self.top + rpsl.nb24s*self.size_y
		for n in xrange(16,256,16):
			x = left+(n*self.size_x)
			content += self._line(x,yt,x,yb,color['black'],True)
			content += self._text(x+4,yt-self.font*2,self.font,color['black'],str(n),'writing-mode="tb"')
		
		# Each inetnum
		v = 0
		id = 0
		javascript = ''
		for row in nrange(cidr[0],cidr[-1],256):
			y = self.top + (v*self.size_y)
			for range in per24.get(row,[]):
				start = tuple(range)[-1]
				size = rpsl.inetnum[range]['length']
				block_size = size
				descr = ' '.join(rpsl.inetnum[range].get('descr',[]))
				remarks = ' '.join(rpsl.inetnum[range].get('remarks',[]))

				wrap = True
				while wrap:
					wrap = True if start + size > 256 else False
					if wrap:
						xl = left + (start*self.size_x)
						xs = 256*self.size_x
						xr = left + xs
						incr = (256 - start)
						size -= incr
						start = 0
					else:
						xl = left + (start*self.size_x)
						xs = size*self.size_x
						xr = xl + xs
						incr = size

					if remarks == 'INFRA-AW':
						border = color['red']
					else:
						border = color['black']

					try:
						back = background[slash[block_size]]
					except KeyError:
						back = color['grey']

					if self.js:
						javascript = '''onmouseover="showPrefix('a%(id)s')" onmouseout="hidePrefix()" onclick="showPrefixAlert('a%(id)s')"''' % {'id':id}
					content += self._rectangle(xl,y,xs,self.size_y,border,back,javascript)

					if len(descr) * self.font / 2  > xs:
						last = max(0,(xs/(self.font/2))-1)
						if last:
							descr = descr[:last] if last < 5 else descr[:last-2] + '..'
						else:
							descr = ''

					if self.js:
						content += self._text(xl+2,y+14,self.font,color['black'],descr,javascript)
					else:
						tps = rpsl.inetnum[range]['netname'] + ["%s - %s" % (rpsl.inetnum[range]['start'],rpsl.inetnum[range]['end'])] + rpsl.inetnum[range].get('descr',[''])
						c,t = self._tooltip(xl+2,y+14,self.font,color['black'],descr,tps,javascript)
						content += c
						tooltips += t
					try:
						self.location[range].append((id,(xl+1,y+1),(xr-1,y+self.size_y-1)))
						id += 1
					except KeyError:
						self.location[range] = [(id,(xl+1,y+1),(xr-1,y+self.size_y-1))]
						id += 1

					if wrap:
						y += self.size_y
			v += 1
		
		with open(self.name,'w+') as w:
			w.write(svg % (content+tooltips))
		
