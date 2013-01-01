
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

def cleanup_shorteners(repo, hosts=["foo.hasb.ug", "bar.hasb.ug"]):
    for h in hosts:
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
        self.assertRaises(validation.ValidationError, do)


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


    def test_subdmain(self):
        withsub = hasbug.Shortener.make("foo.hasb.ug", "http://foo.bugtracker.org/{id}", "http://api.github.com/users/omo")
        self.assertTrue(withsub.is_subdomain)
        self.assertEquals("foo", withsub.subdomain)
        nosub = hasbug.Shortener.make("bar.jp", "http://bar.bugtracker.org/{id}", "http://api.github.com/users/omo")
        self.assertFalse(nosub.is_subdomain)

    def test_guessed_root(self):
        s1 = hasbug.Shortener.make("foo.hasb.ug", "http://foo.bugtracker.org/{id}", "http://api.github.com/users/omo")
        self.assertEquals("http://foo.bugtracker.org/", s1.guessed_root)
        s2 = hasbug.Shortener.make("foo.hasb.ug", "http://foo.bugtracker.org/show_cgi?id={id}", "http://api.github.com/users/omo")
        self.assertEquals("http://foo.bugtracker.org/", s2.guessed_root)
        s3 = hasbug.Shortener.make("foo.hasb.ug", "http://foo.bugtracker.org{id}", "http://api.github.com/users/omo")
        self.assertEquals("http://foo.bugtracker.org", s3.guessed_root)

class PatternSignatureTest(unittest.TestCase):
    def setUp(self):
        self.target_shortener = hasbug.Shortener.make(
            "foo.hasb.ug", "http://foo.bugtracker.org/{id}", "http://github.com/omo")

    def test_compute(self):
        url = "https://bugs.webkit.org/show_bug.cgi?id=101289"
        sig = hasbug.PatternSignature.signature_from_url(url)
        self.assertEquals("bugswebkitorgshowbugcgiid", sig)
        pattern = "https://bugs.webkit.org/show_bug.cgi?id={id}"
        sig = hasbug.PatternSignature.signature_from_pattern(pattern)
        self.assertEquals("bugswebkitorgshowbugcgiid", sig)

    def test_hello(self):
        sig = hasbug.PatternSignature.signature_from_pattern("https://bugs.webkit.org/show_bug.cgi?id={id}")
        target = hasbug.PatternSignature.make(sig)
        self.assertEquals(target.signature, sig)
        target.add("https://bugs.webkit.org/show_bug.cgi?id={id}", "wkb.ug")
        target.add("https://bugs2.webkit.org/show_bug.cgi?id={id}", "wkb2.ug")
        self.assertEquals(2, len(target.patterns))

        self.assertEquals(target.shorten("https://bugs.webkit.org/show_bug.cgi?id=12345"), "http://wkb.ug/12345")
        self.assertEquals(target.shorten("https://bugs2.webkit.org/show_bug.cgi?id=12345"), "http://wkb2.ug/12345")
        def badid():
            target.shorten("https://bugs.webkit.org/show_bug.cgi?id=+++++")
        self.assertRaises(ValueError, badid)
        def nomatch():
            target.shorten("https://bugs3.webkit.org/show_bug.cgi?id=12345")
        self.assertRaises(ValueError, nomatch)

    def test_shorten_shorter_should_win(self):
        pattern = "https://bugs.webkit.org/show_bug.cgi?id={id}"
        target = hasbug.PatternSignature.make(hasbug.PatternSignature.signature_from_pattern(pattern))
        target.add(pattern, "foolong.com")
        target.add(pattern, "foo.com")
        target.add(pattern, "foo.jp")
        self.assertEquals(target.shorten("https://bugs.webkit.org/show_bug.cgi?id=12345"), "http://foo.jp/12345")
