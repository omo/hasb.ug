
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
            self.repo.shorteners.remove_found(s.key)
            self.repo.ownerships.remove_found(s.added_by, s.key)

    def test_add_shortener(self):
        self.repo.add_shortener(self.sfoo)
        self.repo.add_shortener(self.sbar)
