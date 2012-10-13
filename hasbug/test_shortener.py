
import unittest
import hasbug
import hasbug.store as store
import hasbug.testing as testing
import hasbug.validation as validation

def make_fresh():
    return hasbug.Shortener("foo.hasb.ug", "http://foo.bugtracker.org/{id}", "http://github.com/omo")

def make_bad():
    return hasbug.Shortener("foo.hasb.ug", "badurl", "http://github.com/omo")

class MockShortenerTest(unittest.TestCase):
    def setUp(self):
        self.repo = hasbug.MockShorteners()        

    def test_find(self):
        target = self.repo.find("wkb.ug")
        self.assertEquals("https://bugs.webkit.org/show_bug.cgi?id=12345", 
                          target.url_for(12345))

    def test_add(self):
        fresh = make_fresh()
        self.repo.add(fresh)
        self.assertEquals(fresh, self.repo.find(fresh.host))

    def test_add_bad(self):
        bad = make_bad()
        def do():
            self.repo.add(bad)
        self.assertRaises(validation.ValidationError, do)

@unittest.skipIf(not testing.enable_database, "Database test is disabled")
class ShortenerRepoTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo = hasbug.Repo(testing.TABLE_NAME)

    def test_hello(self):
        toadd = make_fresh()
        self.repo.shorteners.add(toadd)
        found = self.repo.shorteners.find("foo.hasb.ug")
        self.assertEquals(found, toadd)
        self.repo.shorteners.remove(found)
        def should_raise():
            self.repo.shorteners.find("foo.hasb.ug")
        self.assertRaises(store.NotFoundError, should_raise)


class ShortenerTest(unittest.TestCase):

    def setUp(self):
        self.target = hasbug.Shortener("foo.hasb.ug", "http://foo.bugtracker.org/{id}", "http://github.com/omo")        

    def test_eq(self):
        b = hasbug.Shortener("foo.hasb.ug", "http://foo.bugtracker.org/{id}", "http://github.com/omo")
        self.assertEquals(self.target, b)

    def test_url_for(self):
        self.assertEquals(self.target.url_for(12345), "http://foo.bugtracker.org/12345")

    def test_validate_good(self):
        self.assertFalse(self.target.validate().invalid())

    def test_validate_bad(self):
        s1 = hasbug.Shortener("foo", 
                              "http://foo.bugtracker.org/{id}", 
                              "http://github.com/omo")        
        self.assertTrue(s1.validate().invalid())

        s2 = hasbug.Shortener("foo.bar.baz", 
                              "bad.url.bugtracker.org/{id}", 
                              "http://github.com/omo")
        self.assertTrue(s2.validate().invalid())

        s3 = hasbug.Shortener("foo.bar.baz", 
                              "https://bugtracker.org/{notid}", 
                              "http://github.com/omo")
        self.assertTrue(s3.validate().invalid())

        s4 = hasbug.Shortener("foo.bar.baz", 
                              "https://bugtracker.org/{notid}", 
                              "notnurl")
        self.assertTrue(s4.validate().invalid())
