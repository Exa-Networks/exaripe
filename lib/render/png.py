import os
import gd
from netaddr import CIDR,nrange

class PNG (object):
	def __init__ (self,allocation,prefix,top,left,right,size_y,size_x):
		self.allocation = allocation
		self.prefix = prefix
		self.right = right
		self.top = top

		self.font = max(1,int(2*size_y/3))
		self.size_y = size_y
		self.size_x = size_x
		self.length = size_x*256

		self.location = {}

		self.name = ''
		self.width = 0
		self.height = 0

	def generate (self,rpsl,dir,name):
		cidr = CIDR(self.allocation)

		self.name = os.path.join(dir,name)
		self.link = os.path.join(self.prefix,name)
		left = (self.font*len(cidr[-1])/5) + 10
		self.width = left + 256*self.size_x + 10
		self.height = (rpsl.nb24s*self.size_y) + self.top + 10
 
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
		image.rectangle((left,self.top),(left+self.length,self.top+(rpsl.nb24s*self.size_y)),color['black'])
		
		# The color legend
		keys = background.keys()
		keys.sort()
		inc = self.width /17
		x = inc
		for k in keys:
			image.rectangle((x-1,4),(x+11,16),color['black'])
			image.filledRectangle((x,5),(x+10,15),background[k])
			image.string(gd.gdFontSmall,(x,25),'/%d' % k,color['black'])
			x += inc
		
		# The horizontal lines
		y = self.top
		ranges = []
		for n in nrange(cidr[0],cidr[-1],256):
			ranges.append((n,y))
			range = str(n)
			t = y + 3
			image.line((left,y),(left+self.length,y),color['black'])
			image.string(gd.gdFontSmall, (left - (self.font*len(range)/2) , t), range, color['black'])
			y+=self.size_y
		
		image.setStyle((color['black'],color['black'],color['black'],gd.gdTransparent,gd.gdTransparent,gd.gdTransparent))
		
		# The horizontal numbering
		yt = self.top - 12
		yb = self.top + rpsl.nb24s*self.size_y
		for n in xrange(0,256,16):
			x = left+(n*self.size_x)
			image.line((x,yt),(x,yb),gd.gdStyled)
			image.stringUp(gd.gdFontSmall,(x,yt),str(n),color['black'])
		
	
		# Each inetnum
		v = 0
		id = 0
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
						xl = left + (start*self.size_x)
						xr = left + (256*self.size_x)
						incr = (256 - start)
						size -= incr
						start = 0
					else:
						xl = left + (start*self.size_x)
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
					if len(descr) * self.font / 2> (xr-xl):
						last = max(0,(xr-xl)/(self.font/2) -1)
						if last:
							descr = descr[:last] if last < 5 else descr[:last-2] + '..'
						else:
							descr = ''
						
					image.string(gd.gdFontSmall,(xl+3,y+3),descr,color['black'])

					try:
						self.location[range].append((id,(xl+1,y+1),(xr-1,y+self.size_y-1)))
						id += 1
					except KeyError:
						self.location[range] = [(id,(xl+1,y+1),(xr-1,y+self.size_y-1))]
						id += 1

					if wrap:
						y += self.size_y
			v += 1
		
		image.writePng(self.name)
		
