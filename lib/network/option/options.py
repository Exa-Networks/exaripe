#!/usr/bin/env python

from __future__ import with_statement

import os
import glob

class Options (dict):
	# Those two variables are what need to be updated by subclasses
	format = {}
	folder = '.'
	
	def __init__ (self):
		self.valid = self.format.keys()

		etc = os.environ.get('ETC','/etc')
		match = os.path.join(etc,'network',self.folder,'[0-9A-Za-z_]*')
		
		for f in glob.glob(match):
			if os.path.isfile(f):
				name = os.path.split(f)[-1]
				content = self._read(f,name)
				if not content is None:
					self[name] = content

	def _read (self,filename,name):
		content = None
		first = True
		try:
			with open(filename) as f:
				for line in [l.strip() for l in f.readlines()]:
					if first:
						if line == "":
							continue
						if line.startswith('#'):
							continue
						if line == "[%s]" % name:
							content = ''
							first = False
							continue
						content = line
						break
					content += line + '\n'
		except IOError:
			content = None
		return content

