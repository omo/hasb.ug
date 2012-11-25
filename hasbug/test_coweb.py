# -*- coding: utf-8 -*-

import unittest, StringIO
import hasbug
import hasbug.coweb
import hasbug.oauth
import hasbug.conf
import hasbug.user
import flask

def fake_urlopen(req):
    if "https://github.com/login/oauth/access_token" == req.get_full_url():
        return StringIO.StringIO('{ "access_token": "mytoken" }')
    if "https://api.github.com/user?access_token=mytoken" == req.get_full_url():
        return StringIO.StringIO(hasbug.user.octocat_text)

class ConsoleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        hasbug.coweb.app.config['DEBUG'] = True
        hasbug.coweb.app.r = hasbug.Repo(name=None)
        hasbug.oauth.urlopen = fake_urlopen

    def login_as_octocat(self):
        with self.app.session_transaction() as sess:
            correct_state = hasbug.coweb.set_auth_state(sess)
        url = "/login/back?code=xxx&state={}".format(correct_state)
        return self.app.get(url)

    def setUp(self):
        self.app = hasbug.coweb.app.test_client()

    def test_oauth(self):
        hasbug.oauth.redirect_url("foobar")

    def assert_redirect_to(self, resp, url):
        self.assertTrue("302" in resp.status)
        redirected_to = resp.headers["Location"]
        self.assertEquals(0, redirected_to.index(url))
        
    def test_login(self):
        resp = self.app.get("/login")
        self.assert_redirect_to(resp, "https://github.com/login/oauth/authorize")

    def test_login_back(self):
        resp = self.login_as_octocat()
        self.assert_redirect_to(resp, "http://localhost/me")

    def test_login_back_wrong_state(self):
        url = "/login/back?code=xxx&state={}".format("wrong_state")
        resp = self.app.get(url)
        self.assertTrue("401" in resp.status)

    def test_user_public(self):
        resp = self.app.get("/~octocat")
        self.assertTrue("200" in resp.status)

    def test_login_user(self):
        self.login_as_octocat()
        with self.app as c:
            c.get("/")
            self.assertEquals(flask.request.user.login, "octocat")

    def test_logout(self):
        self.login_as_octocat()
        with self.app as c:
            c.post("/logout")
            c.get("/")
            self.assertIsNone(flask.request.user)

    def test_me_before_login(self):
        resp = self.app.get("/me")
        self.assert_redirect_to(resp, "http://localhost/login")

    def test_me_after_login(self):
        self.login_as_octocat()
        resp = self.app.get("/me")
        self.assertTrue("octocat" in resp.data)
