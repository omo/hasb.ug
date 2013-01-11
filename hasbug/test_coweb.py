# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import unittest, StringIO, re
import hasbug
import hasbug.coweb
import hasbug.webhelpers
import hasbug.oauth
import hasbug.conf
import hasbug.user
import hasbug.net
import hasbug.app
import flask
import json
import logging

import hasbug.test_shortener as test_shortener

class ConsoleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        hasbug.coweb.app.config['DEBUG'] = True
        hasbug.coweb.app.r = hasbug.Repo(name=None)
        hasbug.coweb.app.logger.setLevel(logging.CRITICAL)
        hasbug.app.fake_static_file_computation()
        hasbug.net.fake_urlopen()
        hasbug.net.add_fake_data("https://github.com/login/oauth/access_token", '{ "access_token": "mytoken" }')
        hasbug.net.add_fake_data("https://api.github.com/user?access_token=mytoken", hasbug.user.octocat_text)
        hasbug.net.add_fake_data('https://www.googleapis.com/urlshortener/v1/url?key=fake',
                                 """
{
 "kind": "urlshortener#url",
 "id": "http://goo.gl/fbsS",
 "longUrl": "http://www.google.com/"
}
""")

    def login_as_octocat(self):
        with self.app.session_transaction() as sess:
            correct_state = hasbug.coweb.set_auth_state(sess)
        url = "/login/back?code=xxx&state={}".format(correct_state)
        return self.app.get(url)

    def setUp(self):
        self.app = hasbug.coweb.app.test_client()
        self.exceeding_shortener_names = [ "foo{0}.com".format(i) for i in range(10) ]
        test_shortener.cleanup_shorteners(hasbug.coweb.app.r, ["foo.hasb.ug", "bar.hasb.ug", "foo.bar"] + self.exceeding_shortener_names)

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

    def test_login_user(self):
        self.login_as_octocat()
        with self.app as c:
            c.get("/")
            self.assertEquals(flask.request.user.login, "octocat")

    def test_logout(self):
        with self.app as c:
            self.login_as_octocat()
            c.post("/logout", data = { "canary": flask.session['canary'] })
            c.get("/")
            self.assertIsNone(flask.request.user)

    def test_me_before_login(self):
        resp = self.app.get("/me")
        self.assert_redirect_to(resp, "http://localhost/login")

    def test_me_after_login(self):
        self.login_as_octocat()
        resp = self.app.get("/me")
        self.assertTrue("200" in resp.status)

    def test_me_with_exceeding_shorteners(self):
        with self.app as c:
            self.login_as_octocat()
            for n in self.exceeding_shortener_names:
                r = self.app.post("/s", data = { "host": n, "pattern": "http://bugs." + n + "/{id}", "canary": flask.session['canary'] })
                self.assertTrue("201" in r.status)
            resp = self.app.get("/me")
            self.assertTrue("200" in resp.status)
            soup = BeautifulSoup(resp.data)
            self.assertEquals(0, len(soup.findAll("div", {'class': re.compile('add-shortener-button')})))
            self.assertEquals(1, len(soup.findAll("div", {'class': re.compile('notice-upper-limit')})))

    def test_shortener_add(self):
        with self.app as c:
            hostvalue = "foo.bar"
            self.login_as_octocat()
            resp = self.app.post("/s", data = { "host": hostvalue, "pattern": "http://bugs.foo.bar/{id}", "canary": flask.session['canary'] })
            self.assertTrue("201" in resp.status)
            self.assertEquals("http://localhost/s/foo.bar", resp.headers.get("location"))
            added = json.loads(resp.data)
            self.assertEquals(added["location"], "/s/foo.bar")

    def test_shortener_add_forbidden(self):
        with self.app as c:
            self.login_as_octocat()
            resp1 = self.app.post("/s", data = { "host": "foo.bar", "pattern": "http://bugs.foo.bar/{id}", "canary": flask.session['canary'] })
            self.assertTrue("201" in resp1.status)
            resp2 = self.app.post("/s", data = { "host": "foo.baz", "pattern": "http://bugs.foo.bar/{id}", "canary": flask.session['canary'] })
            self.assertTrue("403" in resp2.status) # Pattern conflict
            self.assertEquals("pattern", json.loads(resp2.data)["name"])
            resp3 = self.app.post("/s", data = { "host": "foo.bar", "pattern": "http://bugs.foo.baz/{id}", "canary": flask.session['canary'] })
            self.assertTrue("403" in resp3.status) # Host conflict
            self.assertEquals("host", json.loads(resp3.data)["name"])
        
    def test_shortener_show(self):
        s = test_shortener.make_fresh("foo.hasb.ug")
        hasbug.coweb.app.r.add_shortener(s)
        resp = self.app.get("/s/" + s.host)
        self.assert_redirect_to(resp, "http://foo.hasb.ug/")

    def test_shortener_post_no_canary(self):
        with self.app as c:
            self.login_as_octocat()
            resp = self.app.post("/s")
            self.assertTrue("401" in resp.status)

    def test_shortener_delete(self):
        s = test_shortener.make_fresh("foo.hasb.ug", owner=hasbug.user.octocat_dict["url"])
        hasbug.coweb.app.r.add_shortener(s)
        with self.app as c:
            self.login_as_octocat()
            resp = self.app.delete("/s/" + s.host, headers={ "x-hasbug-canary" : flask.session['canary'] })
            self.assertTrue("200" in resp.status)

    def test_show_shorten(self):
        hasbug.coweb.app.r.add_shortener(test_shortener.make_fresh("foo.hasb.ug"))
        resp = self.app.get("/aka/http://foo.bugtracker.org/12345")
        self.assertTrue("200" in resp.status)

    def test_show_shorten_unknown(self):
        hasbug.coweb.app.r.add_shortener(test_shortener.make_fresh("foo.hasb.ug"))
        resp = self.app.get("/aka/http://google.com/")
        self.assertTrue("200" in resp.status)


class BackgroundImageTest(unittest.TestCase):
    def test_hello(self):
        target = hasbug.webhelpers.BackgroundImage('http://farm4.staticflickr.com/3127/3308532489_6a1bbf61fa_b.jpg', "http://www.flickr.com/photos/rnw/3308532489/")
        self.assertEquals(target.credit_name, "rnw")


class StaticFilePathTest(unittest.TestCase):
    def test_hello(self):
        fake_original_path = "foo/baz.jpg"        
        fake_modified_path = "11111111111111111111111111111111.hash/foo/baz.jpg"

        class TestingStaticFilePath(hasbug.app.StaticFilePath):
            def compute_modifiers(self):
                return { fake_original_path: "11111111111111111111111111111111.hash" }

        target = TestingStaticFilePath("myfolder/")
        mod_path = target.to_modified_filename(fake_original_path)
        self.assertEquals(mod_path, fake_modified_path)
        self.assertEquals(target.to_original_filename(mod_path), fake_original_path)
