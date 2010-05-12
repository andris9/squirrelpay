
import os

from tlslite.utils import keyfactory
from tlslite.utils import cryptomath
from tlslite.utils import compat 
from tlslite import X509

import yaml
import cgi
import re
import math

class RequestValidator:
  variableOrder = {
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
    }
  
  def __init__(self):
    self.MACFields = {}
    self.payment_config = yaml.load(open("payment.yaml"), Loader=yaml.Loader)
    self.key_location = os.path.join(os.path.dirname(__file__),"keys")
  
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

  def generateMACString(self):
    data = ''
    for key in self.variableOrder[self.MACFields['VK_SERVICE']]:
      v = self.MACFields[key]
      data += ("%03d" % len(v))+v      
    return data

  def populateMACFields(self, postBody=False, params = False):
    if not params:
      params = cgi.parse_qsl(postBody)
    for i in params:
      k = i[0].decode("latin1")
      v = str(i[1]).decode("latin1")
      if k[:3]=="VK_":
        self.MACFields[k] = v

  def validateIPizzaPayment(self, postBody):
    self.populateMACFields(postBody)

    if self.payment_config["banks"][self.MACFields["VK_SND_ID"]] and \
         self.verifyWithPEM(self.generateMACString().encode("latin1"),
                self.MACFields["VK_MAC"],
                self.payment_config["banks"][self.MACFields["VK_SND_ID"]]['public_key']):
        return self.MACFields["VK_SERVICE"] =='1101'

    else:
      return False

  def genReferenceCode(self, orig_nr):
    weights = [7,3,1]
    nrs = re.findall(r'\d', str(orig_nr))
    nrs.reverse()
    sum = 0
    for i, nr in enumerate(nrs):
      sum = sum + int(nr) * int(weights[i % len(weights)])
    hundred = int(math.ceil(float(sum)/10)*10)
    return "%s%s" %(orig_nr, hundred-sum)
  
  def createIPizzaPayment(self, bank, params):
    self.MACFields["VK_SERVICE"] = '1001'
    self.MACFields["VK_VERSION"] = '008'
    self.MACFields["VK_SND_ID"]  = str(self.payment_config["banks"][bank]['account_id'])
    self.MACFields["VK_ACC"]     = str(self.payment_config["banks"][bank]['account_nr'])
    self.MACFields["VK_NAME"]    = str(self.payment_config["banks"][bank]['account_name'])
    self.MACFields["VK_CURR"]    = str(self.payment_config["currency"])
    self.MACFields["VK_LANG"]    = str(self.payment_config["lang"])
    
    self.populateMACFields(params=params)
    self.MACFields["VK_MAC"] = self.signWithPEM(self.generateMACString().encode("latin1"),
                self.payment_config["banks"][bank]['private_key'])

    form = ''
    for k in self.MACFields.keys():
      form += '<input type="hidden" name="%s" value="%s" />\n' % (k, self.MACFields[k])

    return {"banklink_url": self.payment_config["banks"][bank]['url'], "banklink_form": form}
