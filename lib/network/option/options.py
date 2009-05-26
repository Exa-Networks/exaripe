#!/usr/bin/env python

from __future__ import with_statement

import os
import sys
import time
import glob

class Options (dict):
	# Those two variable are what need to be updated by subclasses
	format = {}
	folder = '.'
	
	def __init__ (self):
		self.valid = self.format.keys()

		etc = os.environ.get('ETC','/etc')
		match = os.path.join(etc,'network',self.folder,'[a-z_]*')

		for file in glob.glob(match):
			if os.path.isfile(file):
				name = os.path.split(file)[-1]
				content = self._read(file,name)
				if not content is None:
					self[name] = content

	def _read (self,file,name):
		content = None
		first = True
		try:
			with open(file) as f:
				for line in [l.strip() for l in f.readlines()]:
					if first:
						if line == "[%s]" % name:
							content = ''
							first = False
							continue
						content = line
						break
					if line == "":
						continue
					if line.startswith('#'):
						continue
					content += line % {'generated':time.strftime("%Y%m%d %H:%M:%S")} + '\n'
		except IOError:
			content = None
		return content

