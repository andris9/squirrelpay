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
    
    if sign.validateIPizzaPayment(self.request.body):
      self.response.out.write("okidoki, makstud %s" % self.request.get("VK_AMOUNT"))
    else:
      self.response.out.write("error")  


class MainHandler(webapp.RequestHandler):

  def get(self):

    self.response.out.write("Squirrelpay!\n")
    
    message = "tere tere"
    amount = 55.10
    stamp = 12345;

    sign = RequestValidator()

    self.response.out.write(cgi.parse_qsl(self.request.body))
    self.response.out.write("\n")
    self.response.out.write(sign.MACFields)

    template_values = sign.createIPizzaPayment("EYP", [
        ['VK_STAMP',  stamp],
        ['VK_AMOUNT', amount],
        ['VK_REF',    sign.genReferenceCode(stamp)],
        ['VK_MSG',    message],
        ['VK_RETURN', "http://squirrelpay.appspot.com/receive"]
    ])
    
    self.response.out.write("<form method='post' action='%s'>%s<input type='submit' name='nupp' value='maksa'/></form>" % (template_values["banklink_url"],template_values["banklink_form"]))
    
    
def main():
  application = webapp.WSGIApplication([('/receive', ReceiveHandler),('/', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
