# -*- coding: utf-8 -*-

import unittest, StringIO
import hasbug
import hasbug.coweb
import hasbug.oauth
import hasbug.conf

user_text = """
{
  "login": "octocat",
  "id": 1,
  "avatar_url": "https://github.com/images/error/octocat_happy.gif",
  "gravatar_id": "somehexcode",
  "url": "https://api.github.com/users/octocat",
  "name": "monalisa octocat",
  "company": "GitHub",
  "blog": "https://github.com/blog",
  "location": "San Francisco",
  "email": "octocat@github.com",
  "hireable": false,
  "bio": "There once was...",
  "public_repos": 2,
  "public_gists": 1,
  "followers": 20,
  "following": 0,
  "html_url": "https://github.com/octocat",
  "created_at": "2008-01-14T04:33:35Z",
  "type": "User"
}
"""

def fake_urlopen(req):
    if "https://github.com/login/oauth/access_token" == req.get_full_url():
        return StringIO.StringIO('{ "access_token": "mytoken" }')
    if "https://api.github.com/user?access_token=mytoken" == req.get_full_url():
        return StringIO.StringIO(user_text)

class ConsoleTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        hasbug.coweb.app.config['DEBUG'] = True
        hasbug.coweb.app.r = hasbug.MockRepo()
        hasbug.oauth.urlopen = fake_urlopen

    def setUp(self):
        self.app = hasbug.coweb.app.test_client()

    def test_oauth(self):
        hasbug.oauth.redirect_url()

    def assert_redirect_to(self, resp, url):
        self.assertTrue("302" in resp.status)
        redirected_to = resp.headers["Location"]
        self.assertEquals(0, redirected_to.index(url))
        
    def test_login_ask(self):
        resp = self.app.get("/login/ask")
        self.assert_redirect_to(resp, "https://github.com/login/oauth/authorize")

    def test_login_back(self):
        correct_state = hasbug.oauth.auth_state()
        url = "/login/back?code=xxx&state={}".format(correct_state)
        resp = self.app.get(url)
        self.assert_redirect_to(resp, "http://localhost/~octocat")

    def test_login_back_wrong_state(self):
        url = "/login/back?code=xxx&state={}".format("wrong_state")
        resp = self.app.get(url)
        self.assertTrue("401" in resp.status)

    def test_user_home(self):
        resp = self.app.get("/~octocat")
        self.assertTrue("200" in resp.status)
