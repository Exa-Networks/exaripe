import os
import gd
from netaddr import CIDR,nrange

class Image (object):
	def __init__ (self,allocation,top,left,right,size_y,size_x):
		self.allocation = allocation
		self.left = left
		self.right = right
		self.top = top

		self.font = 6
		self.size_y = size_y
		self.size_x = size_x
		self.length = size_x*256

		self.location = {}

		self.name = ''
		self.width = 0
		self.height = 0

	def generate (self,rpsl,prefix,name):
		self.name = '%s.png' % name
		self.width = 1050 + self.left
		self.height = (rpsl.nb24s*self.size_y) + self.top + 1 + 100
 
		cidr = CIDR(self.allocation)

		per24 = rpsl.fragment()

		slash = {}
		for s in xrange(24,32+1):
			slash[pow(2,32-s)] = s

		image = gd.image((self.width,self.height))
		
		color = {
			'white' : image.colorAllocate((255, 255, 255)),
			'grey'	: image.colorAllocate((100, 100, 100)),
			'black' : image.colorAllocate((  0,   0,   0)),
			'blue'  : image.colorAllocate((  0,   0, 255)),
			'red'   : image.colorAllocate((255,   0,   0)),
			'green' : image.colorAllocate((0,   255,   0)),
		}
		
		background = {
			32      : image.colorAllocate((230, 230,   0)),
			31      : image.colorAllocate((150, 250,   0)),
			30      : image.colorAllocate((  0, 155,   0)),
			29      : image.colorAllocate((  0, 155,  50)),
			28      : image.colorAllocate((  0, 200, 100)),
			27      : image.colorAllocate((  0, 255, 150)),
			26      : image.colorAllocate((  0, 255, 200)),
			25      : image.colorAllocate((  0, 250, 250)),
			24      : image.colorAllocate((  0, 200, 255)),
			23      : image.colorAllocate((  0, 150, 200)),
			22      : image.colorAllocate((  0, 100, 200)),
			21      : image.colorAllocate((  0,  80, 150)),
			20      : image.colorAllocate((  0,  50, 170)),
			19      : image.colorAllocate((255, 100,   0)),
			18      : image.colorAllocate((255, 200,   0)),
		}
		
		gd.gdMaxColors = 256 * 256 * 256
		
		# The outer box
		image.rectangle((self.left,self.top),(self.left+self.length,self.top+(rpsl.nb24s*self.size_y)),color['black'])
		
		# The color legend
		keys = background.keys()
		keys.sort()
		x = self.left + 100
		for k in keys:
			image.rectangle((x-1,14),(x+11,26),color['black'])
			image.filledRectangle((x,15),(x+10,25),background[k])
			image.string(gd.gdFontSmall,(x+17,14),'/%d' % k,color['black'])
			x += 50
		
		# The horizontal lines
		y = self.top
		ranges = []
		for n in nrange(cidr[0],cidr[-1],256):
			ranges.append((n,y))
			range = str(n)
			t = y + 3
			image.line((self.left,y),(self.left+self.length,y),color['black'])
			image.string(gd.gdFontSmall, (self.left - (self.font * len(range)) - self.font/2, t), range, color['black'])
			y+=self.size_y
		
		image.setStyle((color['black'],color['black'],color['black'],gd.gdTransparent,gd.gdTransparent,gd.gdTransparent))
		
		# The horizontal numbering
		yt = self.top - 12
		yb = self.top + rpsl.nb24s*self.size_y
		for n in xrange(0,256,16):
			x = self.left+(n*self.size_x)
			image.line((x,yt),(x,yb),gd.gdStyled)
			image.stringUp(gd.gdFontSmall,(x,yt),str(n),color['black'])
		
	
		# Each inetnum
		v = 0
		for row in nrange(cidr[0],cidr[-1],256):
			y = self.top + (v*self.size_y)
			for range in per24.get(row,[]):
				start = tuple(range)[-1]
				size = rpsl.inetnum[range]['length']
				descr = ' '.join(rpsl.inetnum[range].get('descr',[]))
				remarks = ' '.join(rpsl.inetnum[range].get('remarks',[]))

				wrap = True
				while wrap:
					wrap = True if start + size > 256 else False
					if wrap:
						xl = self.left + (start*self.size_x)
						xr = self.left + (256*self.size_x)
						incr = (256 - start)
						size -= incr
						start = 0
					else:
						xl = self.left + (start*self.size_x)
						xr = xl + (size*self.size_x)
						incr = size

					image.rectangle((xl,y),(xr,y+self.size_y),color['black'])
					try:
						image.filledRectangle((xl+1,y+1),(xr-1,y+self.size_y-1),background[slash[incr]])
					except KeyError:
						image.filledRectangle((xl+1,y+1),(xr-1,y+self.size_y-1),color['grey'])
					if remarks == 'INFRA-AW':
						image.rectangle((xl+1,y+1),(xr-1,y+self.size_y-1),color['red'])
						image.rectangle((xl+2,y+2),(xr-2,y+self.size_y-2),color['red'])
					if len(descr) * self.font > (xr-xl) - 6:
						descr = descr[:(xr-xl)/self.font -2] + '..'
					image.string(gd.gdFontSmall,(xl+4,y+3),descr,color['black'])

					try:
						self.location[range].append(((xl+1,y+1),(xr-1,y+self.size_y-1)))
					except KeyError:
						self.location[range] = [((xl+1,y+1),(xr-1,y+self.size_y-1))]

					if wrap:
						y += self.size_y
			v += 1
		
		image.writePng(os.path.join(prefix,self.name))
		
