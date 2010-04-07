#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template

class Kifu(db.Model):
    name = db.StringProperty()
    mime = db.StringProperty()
    comment = db.StringProperty(multiline=True)
    size = db.IntegerProperty()
    contents = db.TextProperty()
    author = db.UserProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp.RequestHandler):

  def get(self):
    kifulist = Kifu.all()
    user = users.get_current_user()
    template_values = {
      'user': user,
      'kifulist': kifulist,
      'login_link': users.create_login_url('/')
    }
    tpl = os.path.join(os.path.dirname(__file__),'main.html')
    self.response.out.write(template.render(tpl, template_values))

class UploadHandler(webapp.RequestHandler):
  def post(self):
    file_data = self.request.get('file')
    user = users.get_current_user()
    if not user:
      return self.redirect('/')
    kifu = Kifu(author=user)
    kifu.contents = unicode(file_data,'sjis')
    kifu.name = unicode(self.request.get('kifuname'))
    kifu.put()
    return self.redirect('/')


class KifuHandler(webapp.RequestHandler):
  def get(self,kifuid):
    id = kifuid#self.request.get('id')
    if not id:
      return self.redirect('/')
    
    kifu = Kifu.get_by_id(int(id))
    self.response.out.write(kifu.contents)

class PlayerHandler(webapp.RequestHandler):
  def get(self):
    kifuid = self.request.get('kifuid')
    if not id:
      return self.redirect('/')
    template_values = {
      'kifuid': kifuid,
    }
    tpl = os.path.join(os.path.dirname(__file__),'player.html')
    self.response.out.write(template.render(tpl, template_values))

def main():
  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/upload',UploadHandler),
                                        (r'/kifu/(.*)',KifuHandler),
                                        ('/player',PlayerHandler),
                                       ],debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
