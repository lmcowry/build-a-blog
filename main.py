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
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def get_posts(limit, offset):
    theQuery = "SELECT * FROM blogEntry ORDER BY created DESC LIMIT {0} OFFSET {1}".format(limit, offset)
    allEntries = db.GqlQuery(theQuery)
    return allEntries


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class blogEntry(db.Model):
    # if we give blogEntry without a title, it'll not allow it because we're requiring it
    title = db.StringProperty(required = True)
    theText = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainPage(Handler):
    def render_front(self, title="", theText="", error=""):
        # blogs = db.GqlQuery("SELECT * FROM blogEntry ORDER BY created DESC LIMIT 5")
        blogs = get_posts(5, 0)
        self.render("frontpage5.html", title=title, theText=theText, error=error, blogs=blogs)

    def get(self):
        self.render_front()


class newPost(Handler):
    def render_newPost(self, title="", theText="", error=""):
        self.render("newpost.html", title=title, theText=theText, error=error)

    def get(self):
        self.render_newPost()

    def post(self):
        title = self.request.get("title")
        theText = self.request.get("theText")

        if title and theText:
            a = blogEntry(title = title, theText = theText)
            a.put()
            entryNumberAsString = str(a.key().id())
            entryLink = "/blog/" + entryNumberAsString
            self.redirect(entryLink)

        else:
            error = "we need to both a title and some text!"
            self.render_newPost(title, theText, error)

class ViewPostHandler(Handler):
    def render_specificPost(self, title="", theText="", error=""):
        self.render("specificpost.html", title=title, theText=theText, error=error)

    def get(self, id):
        id = int(id)
        if blogEntry.get_by_id(id) == None:
            self.render_specificPost(error="This is not a valid permalink")
        else:
            thisParticularBlog = blogEntry.get_by_id(id)
            title = thisParticularBlog.title
            # need to add created date?
            theText = thisParticularBlog.theText
            self.render_specificPost(title, theText)






app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
    ('/blog/newpost', newPost)
], debug=True)
