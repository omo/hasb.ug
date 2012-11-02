# -*- coding: utf-8 -*-

import unittest
import hasbug
import hasbug.coweb
import hasbug.oauth

class ConsoleTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        hasbug.coweb.app.r = hasbug.MockRepo()

    def setUp(self):
        self.app = hasbug.coweb.app.test_client()

    def test_oauth(self):
        hasbug.oauth.redirect_url()

    def test_login_auth(self):
        resp = self.app.get("/login/ask")
        self.assertTrue("302" in resp.status)
        redirected_to = resp.headers["Location"]
        self.assertEquals(0, redirected_to.index("https://github.com/login/oauth/authorize"))
