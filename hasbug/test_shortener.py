
import unittest
import hasbug
import hasbug.store as store
import hasbug.testing as testing
import hasbug.validation as validation

def make_fresh(host="foo.hasb.ug", owner="https://api.github.com/users/omo"):
    return hasbug.Shortener.make(host, "http://foo.bugtracker.org/{id}", owner)

def make_fresh_more():
    return hasbug.Shortener.make("bar.hasb.ug", "http://bar.bugtracker.org/{id}", "http://api.github.com/users/omo")

def make_bad():
    return hasbug.Shortener.make("foo.hasb.ug", "bad/url", "https://api.github.com/users/omo")

def cleanup_shorteners(repo, hosts):
    for h in ["foo.hasb.ug", "bar.hasb.ug"]:
        try:
            repo.remove_shortener(repo.shorteners.find(h))
        except store.ItemNotFoundError:
            pass


class ShortenerRepoCommonCases(object):
    def test_list(self):
        self.repo.shorteners.add(make_fresh())
        self.repo.shorteners.add(make_fresh_more())
        listed = self.repo.shorteners.list()
        self.assertTrue("foo.hasb.ug" in [ i.host for i in listed ])
        self.assertTrue("bar.hasb.ug" in [ i.host for i in listed ])

    def test_add_then_remove(self):
        toadd = make_fresh()
        self.repo.shorteners.add(toadd)
        found = self.repo.shorteners.find("foo.hasb.ug")
        self.assertEquals(found, toadd)
        self.repo.shorteners.remove(found)
        def should_raise():
            self.repo.shorteners.find("foo.hasb.ug")
        self.assertRaises(store.ItemNotFoundError, should_raise)

    def test_add_bad(self):
        bad = make_bad()
        def do():
            self.repo.shorteners.add(bad)
        self.assertRaises(validation.ValidationError, do)

    def test_add_unique(self):
        fresh = make_fresh()
        self.repo.shorteners.add(fresh)
        def do():
            self.repo.shorteners.add(fresh)
        self.assertRaises(store.ItemInvalidError, do)


# XXX: Kill this
class MockShortenerRepoTest(unittest.TestCase, ShortenerRepoCommonCases):
    def setUp(self):
        self.repo = hasbug.Repo(name=None)

    def test_find_initials(self):
        target = self.repo.shorteners.find("wkb.ug")
        self.assertEquals("https://bugs.webkit.org/show_bug.cgi?id=12345", 
                          target.url_for(12345))

    def test_remove_by_hostname(self):
        host = "baz.hasb.ug"
        self.repo.shorteners.add(make_fresh(host))
        self.assertIsNotNone(self.repo.shorteners.find(host))
        hasbug.Shortener.remove_by_host(self.repo.shorteners, host)
        def do():
            self.repo.shorteners.find(host)
        self.assertRaises(store.ItemNotFoundError, do)


@unittest.skipIf(not testing.enable_database, "Database test is disabled")
class ShortenerRepoTest(unittest.TestCase, ShortenerRepoCommonCases):
    @classmethod
    def setUpClass(cls):
        cls.repo = hasbug.Repo(testing.TABLE_NAME)

    def setUp(self):
        cleanup_shorteners(self.repo, ["foo.hasb.ug", "bar.hasb.ug"])


class ShortenerTest(unittest.TestCase):
    def setUp(self):
        self.target = hasbug.Shortener.make("foo.hasb.ug", "http://foo.bugtracker.org/{id}", "http://github.com/omo")        

    def test_eq(self):
        b = hasbug.Shortener.make("foo.hasb.ug", "http://foo.bugtracker.org/{id}", "http://github.com/omo")
        self.assertEquals(self.target, b)

    def test_added_by_login(self):
        self.assertEquals(self.target.added_by_login, "omo")

    def test_url_for(self):
        self.assertEquals(self.target.url_for(12345), "http://foo.bugtracker.org/12345")

    def test_validate_good(self):
        self.assertFalse(self.target.validate().invalid())

    def test_validate_bad(self):
        s1 = hasbug.Shortener.make("foo/bar", 
                                   "http://foo.bugtracker.org/{id}", 
                                   "http://github.com/omo")        
        self.assertTrue(s1.validate().invalid())

        s2 = hasbug.Shortener.make("foo.bar.baz", 
                                   "bad.url.bugtracker.org/{id}", 
                                   "http://github.com/omo")
        self.assertTrue(s2.validate().invalid())

        s3 = hasbug.Shortener.make("foo.bar.baz", 
                                   "https://bugtracker.org/{notid}", 
                                   "http://github.com/omo")
        self.assertTrue(s3.validate().invalid())

        s4 = hasbug.Shortener.make("foo.bar.baz", 
                                   "https://bugtracker.org/{notid}", 
                                   "notnurl")
        self.assertTrue(s4.validate().invalid())


class PatternSignatureTest(unittest.TestCase):
    def setUp(self):
        self.target_shortener = hasbug.Shortener.make(
            "foo.hasb.ug", "http://foo.bugtracker.org/{id}", "http://github.com/omo")

    def test_compute(self):
        url = "https://bugs.webkit.org/show_bug.cgi?id=101289"
        sig = hasbug.PatternSignature.compute_from_url(url)
        self.assertEquals("bugswebkitorgshowbugcgiid", sig)

    def test_instantiate(self):
        target = self.target_shortener.make_signature()
        self.assertEquals(self.target_shortener.host, target.host)
        self.assertEquals(self.target_shortener.pattern, target.pattern)

    def test_shorten(self):
        target = self.target_shortener.make_signature()
        self.assertEquals("http://foo.hasb.ug/12345",
                          target.shorten("http://foo.bugtracker.org/12345"))
        def run():
            target.shorten("http://foo.bugtracker.org/+++++")
        self.assertRaises(ValueError, run)
