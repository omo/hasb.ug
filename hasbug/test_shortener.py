
import unittest
import hasbug
import hasbug.store as store
import hasbug.testing as testing

def make_fresh():
    return hasbug.Shortener("foo.hasb.ug", "http://foo.bugtracker.org/{id}", "http://github.com/omo")

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
