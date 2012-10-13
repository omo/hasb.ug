
import unittest
import hasbug
import hasbug.reweb

class RedirectorTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        hasbug.reweb.app.r = hasbug.MockRepo()

    def setUp(self):
        self.app = hasbug.reweb.app.test_client()

    def assert_redirect_to(self, resp, url):
        self.assertTrue("302" in resp.status)
        self.assertEquals(resp.headers["Location"], url)
    
    def test_wkcheckin_hello(self):
        resp = self.app.get("/12345", headers = { "Host": "wkcheck.in" })
        self.assert_redirect_to(resp, "http://trac.webkit.org/changeset/12345")
        resp = self.app.get("/12345", headers = { "Host": "wkb.ug" })
        self.assert_redirect_to(resp, "https://bugs.webkit.org/show_bug.cgi?id=12345")