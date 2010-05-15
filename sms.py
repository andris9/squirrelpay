#!/usr/bin/env python
#!-*- coding:utf-8 -*-


from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db

from fortumo.fortumo import CheckValidRequest, fortumo_config

class ReceiveHandler(webapp.RequestHandler):
  def get(self):

    if not CheckValidRequest(self.request.params):
      self.response.out.write("Invalid request!")
      return
    
    # Database transaction needs to be in a function
    # Transaction is needed for a greater stability -
    #    if DB is currently down, the action is repeated several times
    def insert_sms():
      #msg = Message()
      # "message" needs to be converted from Latin 1 to Unicode
      #msg.message = self.request.get("message")
      #msg.sender = self.request.get("sender")
      #msg.country = self.request.get("country")
      #msg.put()
      pass
    #db.run_in_transaction(insert_sms)
    
    # Response that will be sent back as a SMS, max 120 chars
    self.response.out.write("Message received, thank you!")

class MainHandler(webapp.RequestHandler):

  def get(self):

    self.response.out.write("Hello world SMS!")
    
def main():
  application = webapp.WSGIApplication([('/sms/', MainHandler),
                                        ('/sms/receive', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
