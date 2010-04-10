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
import logging

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
    comment = db.TextProperty()
    author = db.UserProperty()
    author_name = db.StringProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp.RequestHandler):

  def get(self):
    kifulist = Kifu.all()
    user = users.get_current_user()
    template_values = {
      'user': user,
      'kifulist': kifulist,
      'login_link': users.create_login_url('/'),
      'logout_link': users.create_logout_url('/')
    }
    tpl = os.path.join(os.path.dirname(__file__),'templates','main.html')
    self.response.out.write(template.render(tpl, template_values))

class UploadHandler(webapp.RequestHandler):
  def post(self):
    file_data = self.request.get('file')
    user = users.get_current_user()
    if not user:
      return self.redirect('/')
    kifu = Kifu(author=user)
    contents = unicode(file_data,'sjis')
    if contents.find("\r") > 0:
      contents = "\r\n".join(map(lambda line:line.rstrip("\r"),contents.split("\r")))
    kifu.contents = contents
    kifu.name = unicode(self.request.get('kifuname'))
    kifu.author_name = unicode(self.request.get('authorname'))
    kifu.comment = unicode(self.request.get('comment'))
    kifu.put()
    return self.redirect('/')

  def get(self):
    tpl = os.path.join(os.path.dirname(__file__),'templates','upload.html')
    self.response.out.write(template.render(tpl, {}))

class KifuHandler(webapp.RequestHandler):
  def get(self,kifuid):
    if not kifuid:
      return self.redirect('/')
    
    kifu = Kifu.get_by_id(int(kifuid))
    self.response.out.write(kifu.contents)
  
class DeleteKifuHandler(webapp.RequestHandler):
  def get(self,kifuid):
    if not kifuid:
      return self.redirect('/')
    
    kifu = Kifu.get_by_id(int(kifuid))
    if kifu.author == users.get_current_user():
      kifu.delete()
    return self.redirect('/')
  
class PlayerHandler(webapp.RequestHandler):
  def get(self):
    kifuid = self.request.get('kifuid')
    if not kifuid:
      return self.redirect('/')

    kifu = Kifu.get_by_id(int(kifuid))
    comment = ''
    if kifu and kifu.comment:
      comment = kifu.comment
    template_values = {
      'kifuid': kifuid,
      'comment': comment
    }
    tpl = os.path.join(os.path.dirname(__file__),'templates','player.html')
    self.response.out.write(template.render(tpl, template_values))

def main():
  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/upload',UploadHandler),
                                        (r'/kifu/(.*).kifu',KifuHandler),
                                        (r'/deletekifu/(.*)',DeleteKifuHandler),
                                        ('/player',PlayerHandler),
                                       ],debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
