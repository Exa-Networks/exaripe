from __future__ import with_statement

import os
from lxml import etree

class HTML (object):
	def __init__ (self,template,image):
		self.template = template
		self.image = image

	def generate (self,rpsl,location,output):
		attributes = {
			'image' : self.image.name,
			'range' : str(rpsl.range),
		}

		node = etree.parse(self.template)
		style = etree.XSLT(node)

		prefixes = etree.Element ('prefixes',attributes)

		errors = ['there was no error','really none']
		for error in errors:
			etree.SubElement(prefixes,'error').text = error

		id = 0
		for range in rpsl.inetnum.keys():
			data = rpsl.inetnum[range]
			for ((xl,yl),(xr,yr)) in self.image.location[range]:
				prefix = etree.Element ('prefix')

				prefix.set('id',str(id))
				prefix.set('start',str(data['start']))
				prefix.set('end',str(data['end']))

				prefix.set('xl',str(xl))
				prefix.set('xr',str(xr))
				prefix.set('yl',str(yl))
				prefix.set('yr',str(yr))
			
				for description in data.get('descr',['']):
					etree.SubElement(prefix,'description').text = description

				prefix.set('netname',' '.join(data.get('netname','NO NAME')))

				prefixes.append(prefix)
				id += 1

		with open(os.path.join(location,output),'w+') as f:
			f.write(etree.tostring(style.apply(prefixes)))

