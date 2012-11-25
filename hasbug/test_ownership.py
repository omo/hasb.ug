
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
        cls.mojombo = hasbug.User.add_by_login(cls.repo.users, "mojombo")
        cls.sfoo = hasbug.Shortener("foo.com", "http://foo.obug.org/{id}", cls.mojombo.url)
        cls.sbar = hasbug.Shortener("bar.com", "http://bar.obug.org/{id}", cls.mojombo.url)

    def setUp(self):
        for s in [self.sfoo, self.sbar]:
            self.repo.shorteners.remove_found(s.key)
            self.repo.ownerships.remove_found(s.added_by, s.key)

    def test_add_shortener(self):
        hasbug.Ownership.add_shortener(self.repo, self.sfoo)
        hasbug.Ownership.add_shortener(self.repo, self.sbar)
