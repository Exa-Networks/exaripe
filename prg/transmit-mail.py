#!/usr/bin/env python

import os
import sys
from lxml import etree

from network.option.settings import Settings as OptionsSettings
from network.transmit.mailer import Mailer

options = OptionsSettings()

production = True if options['production'].lower() in ['1','true','on'] else False

sent = False
mailer = Mailer()
mailer.mx(options['smtp'])

def messages():
	context = etree.iterparse(sys.stdin)
	for action, elem in context:
		if elem.tag == 'mail':
			yield elem.get('sender'), elem.get('recipient'), elem.get('subject'), elem.text
	raise StopIteration()

for sender,recipient,subject,message in messages():
	if  production:
		print 'sending: mail from: "%s" to: "%s" subject: "%s"' % (sender,recipient,subject)
		mailer.sender(sender)
		mailer.recipient(recipient)
		mailer.subject(subject)
		sent = mailer.send(message)
		
		if not sent:
			print 'could not send mail'
			if mailer.error != None:
				print >> sys.stderr , str(mailer.error)
			else:
				print >> sys.stderr
	else:
		print 'testing: mail from: "%s" to: "%s" subject: "%s"' % (sender,recipient,subject)
		for line in sys.stdin:
			pass

sys.exit(0)
