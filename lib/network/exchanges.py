#!/usr/bin/env python
# encoding: utf-8
"""
exchange.py

Created by Thomas Mangin on 2009-08-19.
Copyright (c) 2009 Exa Networks. All rights reserved.
"""

from netaddr import CIDR,IP

from network.option.options import Options

class _Exchanges (Options):
	folder = 'exchange'
	format = {
	}

class Exchanges (object):
	def __init__ (self):
		self.exchanges = {}
		self.ranges = {}
		
		for k,v in _Exchanges().iteritems():
			ranges = [e for e in v.split('\n') if e]
			self.exchanges[k] = ranges
			for r in ranges:
				self.ranges[r] = k
	
	def list (self):
		return self.exchanges.keys()
	
	def ranges (self,exchange):
		return self.ranges[exchanges]
	
	def name (self,ip):
		for r in self.ranges.keys():
			if IP(ip) in CIDR(r):
				return self.ranges[r]
		return ip
