#!/usr/bin/env python
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
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render (self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blogpost(db.Model):
    title = db.StringProperty(required = True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MakePost(Handler):
    def render_postmaker(self, title="", blogpost="", error=""):
        self.render("newentry.html", title=title, blogpost=blogpost, error=error)

    def get(self):
        self.render_postmaker()

    def post(self):
        title = self.request.get("title")
        blogpost = self.request.get("blogpost")

        if title and blogpost:
            a = Blogpost(title = title, blogpost = blogpost)
            a.put()
            postlink = str(Blogpost.key(a).id())
            self.redirect("/blog/" + postlink)
        else:
            error = "Oops! Please provide a title and post content."
            self.render_postmaker(title, blogpost, error)

class MainPage(Handler):
    def render_front(self, title="", blogpost=""):
        blogposts = db.GqlQuery("SELECT * FROM Blogpost ORDER BY created DESC")
        self.render("front.html", blogposts = blogposts)

    def get(self):
        # postlink = Blogpost.key(Blogpost.blogpost).id()
        # postlink = int(postlink)
        self.render_front()

    def post(self):
        title = self.request.get("title")
        blogpost = self.request.get("blogpost")
        postlink = self.request.get("postlink")
        self.render_front()

class ViewPostHandler(Handler):

    def get(self, id):
        id = int(id)
        single_post = Blogpost.get_by_id(id)
        self.render("permapage.html", post = single_post)

    def post(self):
        self.render_singlepost()

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', MakePost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)
