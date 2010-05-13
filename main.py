#!/usr/bin/env python
#!-*- coding:utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from sqcrypto import RequestValidator
import cgi

class ReceiveHandler(webapp.RequestHandler):

  def post(self):

    sign = RequestValidator()
    
    stamp = sign.checkPayment(self)
    
    if stamp:
      self.response.out.write("okidoki, makstud (%s)" % stamp)
    else:
        self.response.out.write("error")

  def get(self):
    self.post()

class MainHandler(webapp.RequestHandler):

  def get(self):

    self.response.out.write("Squirrelpay!<br />\n")
    
    message = "tere tere"
    amount = 55.49
    stamp = 12345;

    sign = RequestValidator()

    payment = {
        "stamp"  : stamp,
        "amount" : amount,
        "ref"    : sign.genReferenceCode(stamp),
        "message": message,
        "url"    : "http://squirrelpay.appspot.com/receive"
        }

    seb_payment = RequestValidator()
    template_values1 = seb_payment.createPayment("EYP",payment)
    
    nordea_payment = RequestValidator()
    template_values2 = nordea_payment.createPayment("NORDEA",payment)
    
    self.response.out.write("SEB:<br /><form method='post' action='%s'>%s<input type='submit' name='nupp' value='maksa'/></form>" % (template_values1["banklink_url"],template_values1["banklink_form"]))
    self.response.out.write("NORDEA:<br /><form method='post' action='%s'>%s<input type='submit' name='nupp' value='maksa'/></form>" % (template_values2["banklink_url"],template_values2["banklink_form"]))
    
    
def main():
  application = webapp.WSGIApplication([('/receive', ReceiveHandler),('/', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
