#
# fortumo.py
#
# Module to validate incoming messages and deal with the configuration etc.
#
# Copyright (c) 2010 Andris Reinman, andris.reinman@gmail.com
# Licensed under MIT-style license
#

import os
import hashlib
import yaml

#load data from fortumo.yaml
fortumo_config = yaml.load(open(os.path.join(os.getcwd(),"payment.yaml")), Loader=yaml.Loader)["fortumo"]

class RequestValidator:
  allowed_ips = fortumo_config["allowed_ips"]
  service_id = fortumo_config["service_id"]
  secret = fortumo_config["secret"]
  
  def check_ip(self, remote_addr):
    return remote_addr in self.allowed_ips

  def check_service_id(self, service_id):
    #Always return true if API key checking is disabled
    return not self.service_id or self.service_id == service_id
  
  def signature(self, params_array):
    str = ''
    for k in self.ksort(params_array):
      v = params_array[k]
      if k != 'sig':
        str += u"%s=%s" % (k,v)
    str += unicode(self.secret)

    # hashlib doesn't like unicode, so it needs to be encoded
    signature = hashlib.md5(str.encode("utf-8")).hexdigest()
    return signature
  
  def check_signature(self, params_array):
    #Always return true if signature checking is disabled
    if not self.secret:
      return True
    if not "sig" in params_array:
      return False
    return params_array['sig']==self.signature(params_array)
  
  def ksort(self, d, func = None):
    keys = d.keys()
    keys.sort(func)
    return keys

def GenerateSignature(arg_list):
  req = RequestValidator()
  return req.signature(arg_list)

def CheckValidRequest(arg_list):

  req = RequestValidator()
  if not req.check_ip(os.environ['REMOTE_ADDR']):
    return False

  if not 'service_id' in arg_list or not req.check_service_id(arg_list['service_id']):
    return False

  if not req.check_signature(arg_list):
    return False

  return True