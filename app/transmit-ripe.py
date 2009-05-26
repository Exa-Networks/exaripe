#!/usr/bin/env python

import os
import sys

from network.option.ripe import RIPE as OptionsRIPE
from network.transmit.mailer import Mailer

# XXX: Should add command line control here ..

options = OptionsRIPE()

sender = options['sender']
password = options['secret']
production = True if options['production'].lower() in ['1','true','on'] else False

message=''
for line in sys.stdin.readlines():
	message += line
message += '\npassword:       %s' % password

sent = False
mailer = Mailer()
		
if not production:
	print message
	sys.exit(0)

# XXX: Should really perform an DNS MX QUERY here ..
mailer.mx('postman.ripe.net')
mailer.sender(sender)
mailer.recipient('auto-dbm@ripe.net')
mailer.subject('')
sent = mailer.send(message)
		
if not sent:
	print >> sys.stderr , 'could not send ripe update',
	if mailer.error != None:
		print >> sys.stderr , str(mailer.error)
	else:
		print >> sys.stderr
	sys.exit(1)

sys.exit(0)
