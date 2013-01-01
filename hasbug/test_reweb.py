
import unittest
import hasbug
import hasbug.reweb

class RedirectorTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        hasbug.reweb.app.r = hasbug.Repo(name=None)

    def setUp(self):
        self.app = hasbug.reweb.app.test_client()

    def assert_redirect_to(self, resp, url):
        self.assertTrue("302" in resp.status)
        self.assertEquals(resp.headers["Location"], url)
    
    def test_wkcheckin_hello(self):
        resp = self.app.get("/12345", headers = { "Host": "wkcheck.in" })
        self.assert_redirect_to(resp, "http://trac.webkit.org/changeset/12345")
        resp = self.app.get("/12345", headers = { "Host": "wkcheck.in:5000" })
        self.assert_redirect_to(resp, "http://trac.webkit.org/changeset/12345")
        resp = self.app.get("/12345", headers = { "Host": "wkb.ug" })
        self.assert_redirect_to(resp, "https://bugs.webkit.org/show_bug.cgi?id=12345")
        resp = self.app.get("/01234", headers = { "Host": "wkcheck.in" })
        self.assert_redirect_to(resp, "http://trac.webkit.org/changeset/01234")

    def test_wkcheckin_nondigit(self):
        resp = self.app.get("/0123a", headers = { "Host": "wkcheck.in" })
        self.assertTrue("403" in resp.status)

    def test_wkcheckin_root(self):
        resp = self.app.get("/", headers = { "Host": "wkcheck.in" })
        self.assertTrue("200" in resp.status)

    def test_wkcheckin_noop(self):
        resp = self.app.get("/noop", headers = { "Host": "wkcheck.in" })
        self.assertTrue("200" in resp.status)

