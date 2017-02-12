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
    def render_front(self, error="", page=1):
        # blogs = db.GqlQuery("SELECT * FROM blogEntry ORDER BY created DESC LIMIT 5")
        pageNum = 0
        if not (self.request.get('page')):
            pageNum = 1
        else:
            pageNum = self.request.get('page')
        howManyPostsPerPage = 5
        pageNum = int(pageNum)
        theOffset = pageNum * 5 - 5
        blogs = get_posts(howManyPostsPerPage, theOffset)
        totalBlogs = blogs.count()
        currentLastBlog = pageNum * 5
        pageBehind = False
        pageAhead = False
        nextPage = 0
        prevPage = 0
        if pageNum > 1:
            pageBehind = True
            prevPage = pageNum - 1
        if totalBlogs > currentLastBlog:
            pageAhead = True
            nextPage = pageNum + 1

        #check for pages behind.  if it exists, add a string of html

        #check for pages ahead

        # self.response.out.write(blogs.count(offset=originalOffset, limit=howManyPostsPerPage))
        # self.response.out.write(blogs.count())


        # pagesBehind
        # pagesAhead
        #
        # if pagesBehind:
        #     pagesBack = "< previous"
        #
        self.render("frontpage5.html", error=error, blogs=blogs, pageBehind=pageBehind, pageAhead=pageAhead, prevPage=prevPage, nextPage=nextPage)


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
