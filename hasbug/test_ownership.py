
import unittest
import hasbug
import hasbug.store as store
import hasbug.testing as testing
import hasbug.validation as validation
import hasbug.testing_user

class OwnershipTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = hasbug.Repo(testing.TABLE_NAME if testing.enable_database else None)
        cls.mojombo = cls.repo.users.add_by_login("mojombo")
        cls.sfoo = hasbug.Shortener.make("foo.com", "http://foo.obug.org/{id}", cls.mojombo.url)
        cls.sbar = hasbug.Shortener.make("bar.com", "http://bar.obug.org/{id}", cls.mojombo.url)

    def setUp(self):
        for s in [self.sfoo, self.sbar]:
            #self.repo.shorteners.remove_found(s.key)
            #self.repo.ownerships.remove_found(s.added_by, s.key)
            try:
                self.repo.remove_shortener(self.repo.shorteners.find(s.key))
            except store.ItemNotFoundError:
                pass

    def test_add_shortener(self):
        self.repo.add_shortener(self.sfoo)
        self.repo.add_shortener(self.sbar)
        sbar_ownership = self.repo.ownerships.find(self.sbar.added_by, self.sbar.key)
        self.assertEquals(sbar_ownership.owner_key, self.sbar.added_by)

    def test_remove_shortener(self):
        added = self.repo.add_shortener(self.sfoo)
        sfoo_ownership = self.repo.ownerships.find(self.sfoo.added_by, self.sfoo.key)
        self.assertTrue(sfoo_ownership)
        self.repo.remove_shortener(self.sfoo)
        def run():
            self.repo.ownerships.find(self.sfoo.added_by, self.sfoo.key)
        self.assertRaises(hasbug.store.ItemNotFoundError, run)

    @unittest.skipIf(not testing.enable_database, "Database test is disabled - query() needs it.")
    def test_list_belongings(self):
        self.repo.add_shortener(self.sfoo)
        self.repo.add_shortener(self.sbar)
        actual = self.repo.belongings_for(self.mojombo)
        self.assertEquals(len(actual._ownerhips), 2)

    def test_belongings_hello(self):
        o1 = self.repo.add_shortener(self.sfoo)
        o2 = self.repo.add_shortener(self.sbar)
        actual = hasbug.Belongings([o1, o2]).shortener_hosts
        self.assertEquals(["bar.com", "foo.com"], sorted(actual))

    def test_signature_hello(self):
        self.repo.add_shortener(self.sfoo)
        sig = self.repo.pattern_signatures.find_by_url("http://foo.obug.org/12345")
        self.assertEquals(sig.host, self.sfoo.host)
        self.repo.remove_shortener(self.sfoo)
        def run():
            self.repo.pattern_signatures.find_by_url("http://foo.obug.org/+++++")
        self.assertRaises(hasbug.store.ItemNotFoundError, run)
