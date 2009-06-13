#!/usr/bin/env python
# encoding: utf-8
"""
address.py

Created by Thomas Mangin on 2009-06-13.
Copyright (c) 2009 Exa Networks. All rights reserved.
"""

import re
import socket
import struct

_sizetoslash = dict()
_slashtosize = dict()

for bits in xrange(1,32+1):
	size = pow(2,32-bits)
	_sizetoslash[size] = long(bits)
	_slashtosize[bits] = long(size)

# Convert a entry to decimal if octal or hex
def tobase10 (data):
	data = data.lower()
	if data.startswith('0x'):
		return str(int(data,16))
	elif data.startswith('x'):
		return str(int('0'+data,16))
	elif data.startswith('0'):
		return str(int(data,8))
	else:
		return data

def IPv4tolong (ip):
	address = socket.inet_aton(ip)
	unpacked = socket.ntohl(struct.unpack('I', address)[0])
	packed = struct.pack('i', unpacked)
	ordered = struct.unpack('I', packed)[0]
	return ordered

def longtoIPv4 (l):
		value = socket.htonl(l)
		ip = struct.pack('i', value)
		a, b, c, d = struct.unpack('BBBB', ip)
		return '.'.join([i.__str__() for i in a, b, c, d])

#	d = value & 255
#	c = (value >> 8) & 255
#	b = (value >> 16) & 255
#	b = (value >> 24) & 255
#	return '.'.join([a,b,c,d])

#	r = []
#	while l:
#		r.append(str(l&0xFF))
#		l = l>>8
#	return ".".join(r)


# Make sure an ip is of the form a.b.c.d 
# (and not any of its shortcut a.b or a.b.c
# input : string : an ip 
# output : string : an ip
def fixIPv4len (ips):
	b = ips.split('.')
	l = len(b)
	if l == 2: b.extend(['0','0'])
	if l == 3: b.extend(['0'])
	return '.'.join(b)


# Make sure the IP address is not decimal, if so return is a.b.c.d form
# This is a more cpu intensive way to do fixIPv4len as well
def sanitiseIPv4 (ips):
	ips = ips.lower()
	p = ips.split('.')
	l = len(p)
	r = 0
	for i in xrange(l):
		n = tobase10(p[i])
		if not n.isdigit():
			return ips
		v = int(n)
		if i != l-1:
			v = v << (8*(3-i))
		r += v
	return toip(r % 0x100000000)

# is the data an ip of the form a,b,c,d
# input : string : an ip 
# output : boolean : answer
ipchecker = re.compile('^(\d{3}\.){1,3}\d{1,3}$')
def isIPv4(value):
	if ipchecker.match(value):
		return True
	return False

# variant :
# an ip can be a.b.c.d , the common form
# a.b.c which is a shortcut for a.b.c.0
# a.b which is a shortcut for a.b.0.0
ipchecker = re.compile('^(\d{1,3}\.){1,3}\d{1,3}$')
def isUnsanitisedIPv4(value):
	if ipchecker.match(value):
		return True
	return False

# Reverse an ip address for inclusion in an arpa entry
# Input : string : value : an ip under the form a.b.c.d
# Outpout : string : a string d.c.b.a
def IPv4toARPA (ip):
	a,b,c,d = ip.split('.')
	return '.'.join([d, c, b, a])

# XXX: The name of this function really s****
# It answers : Is this number is sum of 2^x number
# Input : integer : size : an ip
# Ouput : boolean : is the ip one of the start of the 32 classless range
def isNetworkSize(size):
	return _sizetoslash.has_key(long(size))

# Can a network start at this ip and be of that size
# Input : integer : network : an IP we want to check if it start a range of lenght size
# Input : integer : size : the size of the network expressed in number of ips
# Outpout : boolean : is the ip of the network the start of a range.
def aligned(network,size):
	return (int(network/size))*size == network

# Decompose a range 328 into the sum of 256 + 64 + 8
# Input : integer : size, the network size to decompose
# Output : list of integer : answer ordered bigger to smaller
def decomposeSize(size):
	start = 1
	result = list()
	loop = True
	while loop:
		for bits in xrange(start,32+1):
			s = tosize(bits)
			if s <= size:
				result.append(s)
				size -= s
				start = bits
				if size == 0:
					loop = False
					break
		if loop:
			raise "Can't decompose size ", size
	return result

# Decompose consecutive ranges into their biggest group
# WARNING: This function expect the size ordered bigger to smaller
# Input : integer : network : a range start
# Input : integer : size : a range lenght
def decomposeRange(network,size):
	# Search for the biggest component of the range
	# if the range is 328 (256 + 64 + 8) we look for 256
	# and store it in boundry
	for bits in xrange(32,0,-1):
		s = tosize(bits)
		if s > size:
			boundry = tosize(bits+1)
			break

	# Look for the ip of ip starting or ending this range
	limit = ((network/boundry)+1)*boundry

	# recursively split the two new ranges until we can not find any way to break them
	if size > 1 and limit > network and limit < network + size:
		parta = decomposeRange(network,limit-network)
		partb = decomposeRange(limit,size-limit+network)
		result = parta
		result.extend(partb)
		return result

	# we want to find how many range their is.
	result = list()
	subsize = decomposeSize(size)
	nb_ranges = len(subsize)
	# if this is a single valid range (ie a valid /something), return it
	if nb_ranges == 1:
		result.append([network,subsize[0]])
		return result

	# Find the biggest netmask possible for the range start we have just found
	while nb_ranges:
		# size in the list are ordered bigger to smaller
		# Is that tmpsize buffer really needed ? (may well be needed to not kill the code in next versions)
		tmpsize = copy(subsize)
		for s in subsize:
			if aligned(network,s):
				tmpsize.remove(s)
				result.append([network,s])
				network += s
				break
		subsize = tmpsize
		# is the test necessary ?? was surely here to catch some bug but now ?
		if nb_ranges != len(subsize):
			nb_ranges = len(subsize)
		else:
			raise "Can not get here", str(toip(network)) + " " + str(size) + " " + str(subsize)
	return result

# return the /size format of a netmask
def IPv4NetmaskToBits(netmask):
	return _sizetoslash[4294967296 - IPv4tolong(netmask)]

# return the /size format of a netmask
def IPv4NetmaskToSize(netmask):
	return _slashtosize[IPv4NetmaskToBits(netmask)]

def IPv4bitsToNetmask(bits):
	if not 0 <= bits <= 32:
		raise ValueError, 'invalid size for netmask'

	value = (2**bits - 1) << (32 - bits)
	netmask = longtoIPv4(value)
	return netmask

# return the network of a range given an IP and a netmask
def IPv4NetworkNetmask (ip,netmask):
	l = IPv4tolong(ip)
	s = IPv4NetmaskToSize(netmask)
	m = l / s
	return longtoIPv4(m*s)

# return the network of a range given an IP and a netmask
def IPv4NetworkBits (ip,bits):
	l = IPv4tolong(ip)
	s = IPv4BitsToSize(bits)
	m = l / s
	return longtoIPv4(m*s)
