#!/usr/bin/env python
#!-*- coding:utf-8 -*-
#

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from banklink.sqcrypto import RequestValidator, genReferenceCode, payment_config
import cgi

from google.appengine.ext import db
import dbtables

class ReceiveHandler(webapp.RequestHandler):

  def post(self):

    sign = RequestValidator()
    
    stamp = sign.checkPayment(self)
    
    if stamp["result"]:
      self.response.out.write("okidoki, makstud (%s)" % stamp["id"])
    else:
      self.response.out.write("error (%s)" % stamp["id"])

  def get(self):
    self.post()

class MainHandler(webapp.RequestHandler):

  def get(self):

    self.response.out.write("Squirrelpay!<br />\n")
    
    message = "tere tere"
    amount = 55.49
    stamp = 12345;

    payment_data = {
        "stamp"  : stamp,
        "amount" : amount,
        "ref"    : genReferenceCode(stamp),
        "message": message,
        "url"    : "http://squirrelpay.appspot.com/receive"
        }

    for k in payment_config["banks"].keys():
      bank = k
      if payment_config["banks"][k]["active"]:
        payment = RequestValidator()
        template_values = payment.createPayment(bank,payment_data)   
        self.response.out.write("%s:<br /><form method='post' action='%s'>%s<input type='submit' name='nupp' value='maksa'/></form>" % (bank, template_values["banklink_url"],template_values["banklink_form"]))
    
    
def main():
  application = webapp.WSGIApplication([('/receive', ReceiveHandler),('/', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
