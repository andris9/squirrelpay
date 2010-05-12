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
    self.response.out.write("hallo hallo")
    self.response.out.write(self.request.__dict__)

    VK_MAC = self.request.get('VK_MAC')
    
    params = cgi.parse_qs(self.request.body)
    
    VK_SERVICE= params['VK_SERVICE'][0].decode("latin1")
    VK_VERSION = params['VK_VERSION'][0].decode("latin1")
    VK_SND_ID = params['VK_SND_ID'][0].decode("latin1")
    VK_REC_ID = params['VK_REC_ID'][0].decode("latin1")
    VK_STAMP = params['VK_STAMP'][0].decode("latin1")
    VK_T_NO = params['VK_T_NO'][0].decode("latin1")
    VK_AMOUNT = params['VK_AMOUNT'][0].decode("latin1")
    VK_CURR = params['VK_CURR'][0].decode("latin1")
    VK_REC_ACC = params['VK_REC_ACC'][0].decode("latin1")
    VK_REC_NAME = params['VK_REC_NAME'][0].decode("latin1")
    VK_SND_ACC = params['VK_SND_ACC'][0].decode("latin1")
    VK_SND_NAME = params['VK_SND_NAME'][0].decode("latin1")
    VK_REF = params['VK_REF'][0].decode("latin1")
    VK_MSG = params['VK_MSG'][0].decode("latin1")
    VK_T_DATE = params['VK_T_DATE'][0].decode("latin1")
    
    self.response.out.write("\n")
    self.response.out.write(self.request.body)
    self.response.out.write("\n")

    self.response.out.write(params)
    
    self.response.out.write("\n")
    self.response.out.write(self.request.get('VK_SND_NAME'))
    self.response.out.write("\n")
    self.response.out.write(self.request.get('VK_SND_NAME').decode())
    self.response.out.write("\n")
    
    self.response.out.write(""""
    $mac["VK_SERVICE"] = "%s";
    $mac["VK_VERSION"] = "%s";
    $mac["VK_SND_ID"] = "%s";
    $mac["VK_REC_ID"] = "%s";
    $mac["VK_STAMP"] = "%s";
    $mac["VK_T_NO"] = "%s";
    $mac["VK_AMOUNT"] = "%s";
    $mac["VK_CURR"] = "%s";
    $mac["VK_REC_ACC"] = "%s";
    $mac["VK_REC_NAME"] = "%s";
    $mac["VK_SND_ACC"] = "%s";
    $mac["VK_SND_NAME"] = "%s";
    $mac["VK_REF"] = "%s";
    $mac["VK_MSG "] = "%s";
    $mac["VK_T_DATE"] = "%s";
    $mac["VK_MAC"] = "%s";
""" % (VK_SERVICE, VK_VERSION, VK_SND_ID, VK_REC_ID, VK_STAMP, VK_T_NO, VK_AMOUNT, VK_CURR, VK_REC_ACC, VK_REC_NAME, VK_SND_ACC, VK_SND_NAME, VK_REF, VK_MSG, VK_T_DATE, VK_MAC))
    
    ret = ("%03d" % len(VK_SERVICE))+VK_SERVICE + \
      ("%03d" % len(VK_VERSION))+VK_VERSION + \
        ("%03d" % len(VK_SND_ID))+VK_SND_ID + \
          ("%03d" % len(VK_REC_ID))+VK_REC_ID + \
            ("%03d" % len(VK_STAMP))+VK_STAMP + \
              ("%03d" % len(VK_T_NO))+VK_T_NO + \
                ("%03d" % len(VK_AMOUNT))+VK_AMOUNT + \
                  ("%03d" % len(VK_CURR))+VK_CURR + \
                    ("%03d" % len(VK_REC_ACC))+VK_REC_ACC + \
                      ("%03d" % len(VK_REC_NAME))+VK_REC_NAME + \
                        ("%03d" % len(VK_SND_ACC))+VK_SND_ACC + \
                          ("%03d" % len(VK_SND_NAME))+VK_SND_NAME + \
                            ("%03d" % len(VK_REF))+VK_REF + \
                              ("%03d" % len(VK_MSG))+VK_MSG + \
                                ("%03d" % len(VK_T_DATE))+VK_T_DATE
                
    self.response.out.write("\n\n")
    self.response.out.write(ret)
    
    self.response.out.write("\n\n")
    self.response.out.write(VK_MAC)

    self.response.out.write("\n\n")

    sign = RequestValidator()
    if sign.verifyWithPEM(ret.encode("latin1"), VK_MAC, "test_seb_pub.pem"):
      self.response.out.write("okidoki")
    else:
      self.response.out.write("error")  


class MainHandler(webapp.RequestHandler):

  def get(self):
    
    sign = RequestValidator()
    
    self.response.out.write("Squirrelpay!\n")
    data = "tere tere"

    self.response.out.write("<pre>\n")

    signature = sign.signWithPEM(data,"test_seb_private.pem")
    self.response.out.write(signature+"\n")
    
    if sign.verifyWithPEM(data, signature, "test_seb_pub.pem"):
      self.response.out.write("Signature OK\n")
    else:
      self.response.out.write("Signature NOT OK\n")
    
    self.response.out.write("</pre>\n")
      
    my_id = 'testvpos'
    account_number = '10002050618003'
    account_owner = 'Keegi'
    banklink_address= 'https://www.seb.ee/cgi-bin/dv.sh/un3min.r'
    #return_addr = "http://www.webamp.me/squirrelpay/receive.php"
    return_addr = "http://squirrelpay.appspot.com/receive"

    VK_SERVICE = '1001'
    VK_VERSION = '008'
    VK_SND_ID = "%s" % my_id
    VK_STAMP= "%s" % 12345
    VK_AMOUNT  = "%s" % 55
    VK_CURR = "EEK"
    VK_ACC  = "%s" % account_number
    VK_NAME = "%s" % account_owner
    VK_REF  = "%s" % 1232
    VK_MSG  = "tere tere"
    VK_RETURN  = "%s" % return_addr
    VK_LANG = "EST"
    
    ret = ("%03d" % len(VK_SERVICE))+VK_SERVICE + \
      ("%03d" % len(VK_VERSION))+VK_VERSION + \
        ("%03d" % len(VK_SND_ID))+VK_SND_ID + \
          ("%03d" % len(VK_STAMP))+VK_STAMP + \
            ("%03d" % len(VK_AMOUNT))+VK_AMOUNT + \
              ("%03d" % len(VK_CURR))+VK_CURR + \
                ("%03d" % len(VK_ACC))+VK_ACC + \
                  ("%03d" % len(VK_NAME))+VK_NAME + \
                    ("%03d" % len(VK_REF))+VK_REF + \
                      ("%03d" % len(VK_MSG))+VK_MSG
    
    VK_MAC = sign.signWithPEM(ret,"test_seb_private.pem")
    
    self.response.out.write("""
R: %s<br />
<form method="post" action="%s">
<input type="text" name="VK_SERVICE" value="%s" /><br />
<input type="text" name="VK_VERSION" value="%s" /><br />
<input type="text" name="VK_SND_ID" value="%s" /><br />
<input type="text" name="VK_STAMP" value="%s" /><br />
<input type="text" name="VK_AMOUNT" value="%s" /><br />
<input type="text" name="VK_CURR" value="%s" /><br />
<input type="text" name="VK_ACC" value="%s" /><br />
<input type="text" name="VK_NAME" value="%s" /><br />
<input type="text" name="VK_REF" value="%s" /><br />
<input type="text" name="VK_MSG" value="%s" /><br />
<input type="text" name="VK_RETURN" value="%s" /><br />
<input type="text" name="VK_LANG" value="%s" /><br />
<input type="text" name="VK_MAC" value="%s" /><br />
<input type="submit" name="nupp" value="mine" /><br />
</form>
    """ % (ret, banklink_address, VK_SERVICE, VK_VERSION, VK_SND_ID, VK_STAMP, VK_AMOUNT, VK_CURR, VK_ACC, VK_NAME, VK_REF, VK_MSG, VK_RETURN, VK_LANG, VK_MAC))

def main():
  application = webapp.WSGIApplication([('/receive', ReceiveHandler),('/', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
