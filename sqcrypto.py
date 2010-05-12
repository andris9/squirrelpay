
import os

from tlslite.utils import keyfactory
from tlslite.utils import cryptomath
from tlslite.utils import compat 
from tlslite import X509

class RequestValidator:
  key_location = os.path.join(os.path.dirname(__file__),"keys/")
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

    print "\n\n"
    
    print publickey
    
    print "\n\n"
    
    print decoded_sig

    print "\n\n"
    
    print compat.stringToBytes(data)

    print "\n\n - "

    print publickey.verify(decoded_sig, compat.stringToBytes(data))

    print "\n\n - "
    
    print publickey.hashAndVerify(decoded_sig, compat.stringToBytes(data))

    print "\n\n - "


    return publickey.hashAndVerify(decoded_sig, compat.stringToBytes(data))