
import unittest
import hasbug
import hasbug.store as store
import hasbug.testing as testing
import hasbug.validation as validation
import hasbug.user as user

if not testing.enable_database:
    user.fake_urlopen()
    user.add_fake_mojombo_to_urlopen()

class UserRepoCommonCases(object):
    def test_add_twice(self):
        target = hasbug.User(user.octocat_dict)
        self.repo.users.add(target, can_replace=True)
        self.repo.users.add(target, can_replace=True)
        self.assertEquals(self.repo.users.find(target.key).login, target.login)

    def test_add_by_login(self):
        login = "mojombo"
        self.repo.users.add_by_login(login)
        self.assertEquals(self.repo.users.find(hasbug.User.url_from_login(login)).login, login)


@unittest.skipIf(not testing.enable_database, "Database test is disabled")
class UserRepoTest(unittest.TestCase, UserRepoCommonCases):
    @classmethod
    def setUpClass(cls):
        cls.repo = hasbug.Repo(testing.TABLE_NAME)

    def setUp(self):
        try:
            self.repo.users.remove_by_url(user.octocat_dict["url"])
        except store.ItemNotFoundError:
            pass


class MockUserRepoTest(unittest.TestCase, UserRepoCommonCases):
    def setUp(self):
        self.repo = hasbug.Repo(name=None)
