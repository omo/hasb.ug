
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
        foo_pattern = "http://foo.obug.org/{id}"
        cls.sfoo = hasbug.Shortener.make("foo.com", foo_pattern, cls.mojombo.url)
        cls.sbar = hasbug.Shortener.make("bar.com", "http://bar.obug.org/{id}", cls.mojombo.url)
        cls.sbaz = hasbug.Shortener.make("baz.com", "http://foo2.obug.org/{id}", cls.mojombo.url)

        cls.sfoo_longer = hasbug.Shortener.make("foolong.com", foo_pattern, cls.mojombo.url)
        cls.sfoo_shorter = hasbug.Shortener.make("foo.jp", foo_pattern, cls.mojombo.url)
        cls.sfoo_similar = hasbug.Shortener.make("foo.edu", foo_pattern, cls.mojombo.url)

    def setUp(self):
        for s in [self.sfoo, self.sbar, self.sbaz]:
            try:
                self.repo.remove_shortener(self.repo.shorteners.find(s.key))
            except store.ItemNotFoundError:
                pass

    def test_add_shortener(self):
        self.repo.add_shortener(self.sfoo)
        self.repo.add_shortener(self.sbar)
        sbar_ownership = self.repo.ownerships.find(self.sbar.added_by, self.sbar.key)
        self.assertEquals(sbar_ownership.owner_key, self.sbar.added_by)

    def test_add_conflict_longer(self):
        self.repo.add_shortener(self.sfoo)
        def run():
            self.repo.add_shortener(self.sfoo_longer)
        self.assertRaises(validation.ValidationError, run)

    def test_add_conflict_similar(self):
        self.repo.add_shortener(self.sfoo)
        def run():
            self.repo.add_shortener(self.sfoo_similar)
        self.assertRaises(validation.ValidationError, run)

    def test_add_not_conflict_shorter(self):
        self.repo.add_shortener(self.sfoo)
        self.repo.add_shortener(self.sfoo_shorter)
        

    def test_remove_shortener(self):
        self.repo.add_shortener(self.sfoo)
        sfoo_ownership = self.repo.ownerships.find(self.sfoo.added_by, self.sfoo.key)
        self.assertTrue(sfoo_ownership)
        self.repo.remove_shortener(self.sfoo)
        def run():
            self.repo.ownerships.find(self.sfoo.added_by, self.sfoo.key)
        self.assertRaises(hasbug.store.ItemNotFoundError, run)

    def test_update_shortener(self):
        self.repo.add_shortener(self.sfoo)
        self.repo.update_shortener(self.sfoo)

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
        url = "http://foo.obug.org/12345"
        self.repo.add_shortener(self.sfoo)
        self.repo.add_shortener(self.sbaz)
        sig = self.repo.pattern_signatures.find_by_url(url)
        self.assertTrue(self.sfoo.host in sig.patterns.keys())
        self.assertTrue(self.sbaz.host in sig.patterns.keys())

        # Signature can conflict
        url2 = "http://foo2.obug.org/12345"
        sig2 = self.repo.pattern_signatures.find_by_url(url2)
        self.assertTrue(self.sfoo.host in sig2.patterns.keys())
        self.assertTrue(self.sbaz.host in sig2.patterns.keys())

        # Even after removal, signatures (now empty) remain.
        self.repo.remove_shortener(self.sfoo)
        self.repo.remove_shortener(self.sbaz)

        sig3 = self.repo.pattern_signatures.find_by_url(url)
        self.assertTrue(self.sfoo.host not in sig3.patterns.keys())
        self.assertTrue(self.sbaz.host not in sig3.patterns.keys())
