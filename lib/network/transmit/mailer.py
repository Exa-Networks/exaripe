#!/usr/bin/env python
from email.MIMEText import MIMEText
from smtplib import SMTP
import time

class Mailer (object):
	def __init__(self, gpg=None):
		self._gpg = gpg
		self.error = None
		self._mx = "postman.ripe.net"
		self._subject = None
		self._sender = None
		self._recipient = None
	
	def gpg (self,gpg):
		self._gpg = gpg
	
	def mx (self,mx):
		self._mx = mx
	
	def subject (self,subject):
		self._subject = subject
	
	def sender (self,sender):
		self._sender = sender
	
	def recipient (self,recipient):
		self._recipient = recipient
	
	def send (self,message,subject=None,sender=None,recipient=None):
		if subject == None: subject = self._subject
		if sender == None: sender = self._sender
		if recipient == None: recipient = self._recipient
		
		if not recipient:
			self.error = 'No recipient'
			return False
		
		if not sender:
			self.error = 'No sender'
			return False
		
		if subject == None:
			self.error = 'No subject'
			return False
		
		self.error = None
		if self._gpg:
			message = self._gpg.clearsign(message)
			if self._gpg.error:
				self.error = 'could not gpg sign/encrypt the email content : ' + str(self._gpg.error)
				return False
		
		msg = MIMEText(message)
		msg['Subject'] = subject
		msg['From'] = sender
		msg['To'] = recipient
		msg['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S %Z",time.localtime())
		
		try:
			smtp = SMTP(self._mx,25,self._mx)
			if type(recipient) == type(""):
				recipient = [recipient]
			smtp.sendmail(sender,recipient,msg.as_string())
			smtp.close()
		except:
			self.error = 'problem sending mail'
			return False
		
		return True

