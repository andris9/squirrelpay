
import os

from tlslite.utils import keyfactory
from tlslite.utils import cryptomath
from tlslite.utils import compat 
from tlslite import X509

import yaml
import cgi
import re
import math
import hashlib

class RequestValidator:
  variableOrder = {
    "iPizza":{
      "1001": [
         'VK_SERVICE','VK_VERSION','VK_SND_ID',
         'VK_STAMP','VK_AMOUNT','VK_CURR',
         'VK_ACC','VK_NAME','VK_REF','VK_MSG'
        ],
      "1101": [
         'VK_SERVICE','VK_VERSION','VK_SND_ID',
         'VK_REC_ID','VK_STAMP','VK_T_NO','VK_AMOUNT','VK_CURR',
         'VK_REC_ACC','VK_REC_NAME','VK_SND_ACC','VK_SND_NAME',
         'VK_REF','VK_MSG','VK_T_DATE'
        ],
      "1901": [
         'VK_SERVICE','VK_VERSION','VK_SND_ID',
         'VK_REC_ID','VK_STAMP','VK_REF','VK_MSG'
        ]
      },
    "SOLO": {
      "OUT": [
         'SOLOPMT_VERSION','SOLOPMT_STAMP','SOLOPMT_RCV_ID',
         'SOLOPMT_AMOUNT','SOLOPMT_REF','SOLOPMT_DATE',
         'SOLOPMT_CUR'
        ],
      "IN":[
         'SOLOPMT_RETURN_VERSION','SOLOPMT_RETURN_STAMP',
         'SOLOPMT_RETURN_REF','SOLOPMT_RETURN_PAID'
        ]
      }
    }
  
  def __init__(self):
    self.MACFields = {}
    self.payment_config = yaml.load(open("payment.yaml"), Loader=yaml.Loader)
    self.key_location = os.path.join(os.path.dirname(__file__),"keys")
    self.service_id = False
    self.cert = False
  
  def signWithPEM(self, data, key_file):
    
    file = open(os.path.join(self.key_location,key_file))
    pem = file.read()
    file.close()
    
    key = keyfactory.parsePEMKey(pem, private=True)
    signature = key.hashAndSign(compat.stringToBytes(data)) 
    return cryptomath.bytesToBase64(signature) 
  
  def verifyWithPEM(self, data, signature, key_file):

    file = open(os.path.join(self.key_location,key_file))
    pem = file.read()
    file.close()
    
    decoded_sig = cryptomath.base64ToBytes(signature)
    
    x5 = X509.X509()
    x5.parse(pem)        
    publickey = x5.publicKey

    return publickey.hashAndVerify(decoded_sig, compat.stringToBytes(data))

  def generateIPizzaMACString(self):
    data = ''
    for key in self.variableOrder["iPizza"][self.MACFields['VK_SERVICE']]:
      v = self.MACFields[key]
      data += ("%03d" % len(v))+v      
    return data

  def generateSOLOMACString(self):
    data = ''
    for key in self.variableOrder["SOLO"][self.service_id]:
      if key in self.MACFields:
        v = self.MACFields[key]
      else:
        v = ""
      data += "%s&" % v
    return hashlib.md5("%s%s&" %(data,self.cert)).hexdigest().upper()

  def generateMACString(self, type):
    if type=="iPizza":
      return self.generateIPizzaMACString()
    if type=="SOLO":
      return self.generateSOLOMACString()

  def populateMACFields(self, postBody=False, params = False):
    if not params:
      params = cgi.parse_qsl(postBody)
    for i in params:
      k = i[0].decode("latin1")
      v = str(i[1]).decode("latin1")
      if k[:3]=="VK_" or k[:8]=="SOLOPMT_":
        self.MACFields[k] = v

  def validateIPizzaPayment(self, postBody):
    self.populateMACFields(postBody)

    if self.payment_config["banks"][self.MACFields["VK_SND_ID"]] and \
         self.verifyWithPEM(self.generateMACString("iPizza").encode("latin1"),
                self.MACFields["VK_MAC"],
                self.payment_config["banks"][self.MACFields["VK_SND_ID"]]['public_key']):
        return self.MACFields["VK_SERVICE"] =='1101' and self.MACFields["VK_STAMP"]
    else:
      return False

  def validateSOLOPayment(self, bank, queryStr):
    
    self.service_id = 'IN'
    file = open(os.path.join(self.key_location,self.payment_config["banks"][bank]['private_key']))
    self.cert = file.read()
    file.close()
      
    self.populateMACFields(queryStr)
    return "SOLOPMT_RETURN_PAID" in self.MACFields and len(self.MACFields["SOLOPMT_RETURN_PAID"]) and \
          self.generateMACString("SOLO") == self.MACFields["SOLOPMT_RETURN_MAC"] and \
              self.MACFields["SOLOPMT_RETURN_STAMP"]

  def genReferenceCode(self, orig_nr):
    weights = [7,3,1]
    nrs = re.findall(r'\d', str(orig_nr))
    nrs.reverse()
    sum = 0
    for i, nr in enumerate(nrs):
      sum = sum + int(nr) * int(weights[i % len(weights)])
    hundred = int(math.ceil(float(sum)/10)*10)
    return "%s%s" %(orig_nr, hundred-sum)
  
  def createPaymentForm(self):
    form = ''
    for k in self.MACFields.keys():
      form += '<input type="hidden" name="%s" value="%s" />\n' % (k, self.MACFields[k])
    return form
  
  def createIPizzaPayment(self, bank, params):
    self.MACFields["VK_SERVICE"] = '1001'
    self.MACFields["VK_VERSION"] = '008'

    self.MACFields["VK_SND_ID"]  = str(self.payment_config["banks"][bank]['account_id'])
    self.MACFields["VK_ACC"]     = str(self.payment_config["banks"][bank]['account_nr'])
    self.MACFields["VK_NAME"]    = str(self.payment_config["banks"][bank]['account_name'])
    self.MACFields["VK_CURR"]    = str(self.payment_config["currency"])
    self.MACFields["VK_LANG"]    = str(self.payment_config["lang"])
    
    self.MACFields["VK_STAMP"]   = str(params["stamp"])
    self.MACFields["VK_AMOUNT"]  = str(params["amount"])
    self.MACFields["VK_REF"]     = str(params["ref"])
    self.MACFields["VK_MSG"]     = str(params["message"])
    self.MACFields["VK_RETURN"]  = str(params["url"])
    
    self.MACFields["VK_MAC"] = self.signWithPEM(self.generateMACString("iPizza").encode("latin1"),
                self.payment_config["banks"][bank]['private_key'])

    return {"banklink_url": self.payment_config["banks"][bank]['url'],
            "banklink_form": self.createPaymentForm()}

  def createSOLOPayment(self, bank, params):
    langs = {"ENG":3, "EST":4, "LAT":6, "LIT":7, "RUS":4}
    self.service_id = 'OUT'

    file = open(os.path.join(self.key_location,self.payment_config["banks"][bank]['private_key']))
    self.cert = file.read()
    file.close()
      
    self.MACFields["SOLOPMT_VERSION"] = '0003'
    self.MACFields["SOLOPMT_RCV_ID"] =  str(self.payment_config["banks"][bank]['account_id'])
    self.MACFields["SOLOPMT_STAMP"] = str(params["stamp"])
    self.MACFields["SOLOPMT_AMOUNT"] =  str(params["amount"])
    self.MACFields["SOLOPMT_CUR"] = str(self.payment_config["currency"])
    self.MACFields["SOLOPMT_DATE"] = 'EXPRESS'
    self.MACFields["SOLOPMT_CONFIRM"] = 'YES'
    self.MACFields["SOLOPMT_REF"] = str(params["ref"])
    self.MACFields["SOLOPMT_MSG"] = str(params["message"])
    self.MACFields["SOLOPMT_RETURN"] = str(params["url"])
    self.MACFields["SOLOPMT_CANCEL"] = str(params["url"])
    self.MACFields["SOLOPMT_REJECT"] = str(params["url"])
    self.MACFields["SOLOPMT_LANGUAGE"] = langs[self.payment_config["lang"]]
    self.MACFields["SOLOPMT_KEYVERS"] = '0001'
      
    self.MACFields["SOLOPMT_MAC"] = self.generateSOLOMACString()
           
    return {"banklink_url": self.payment_config["banks"][bank]['url'],
            "banklink_form": self.createPaymentForm()}
      
  def createPayment(self, bank, params):
    if self.payment_config["banks"][bank]['type']=="iPizza":
      return self.createIPizzaPayment(bank, params)
    if self.payment_config["banks"][bank]['type']=="SOLO":
      return self.createSOLOPayment(bank, params)


  def checkPayment(self, requestObj):
    if requestObj.request.get("VK_STAMP"):
      return self.validateIPizzaPayment(requestObj.request.body)
    elif requestObj.request.get("SOLOPMT_RETURN_STAMP"):
      return self.validateSOLOPayment("NORDEA", requestObj.request.query_string)
    else:
      return False