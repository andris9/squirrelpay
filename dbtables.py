
from google.appengine.ext import db

class SqUser(db.Model):
  username = db.StringProperty()
  password = db.StringProperty()
  time = db.DateTimeProperty(auto_now_add = True)
  money = db.IntegerProperty(default = 0)