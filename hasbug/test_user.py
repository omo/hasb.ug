
import unittest
import hasbug
import hasbug.store as store
import hasbug.testing as testing
import hasbug.validation as validation
import hasbug.user as user

class UserRepoCommonCases(object):
    def test_add_twice(self):
        target = hasbug.User(user.octocat_dict)
        self.repo.users.add(target, can_replace=True)
        self.repo.users.add(target, can_replace=True)
        self.assertEquals(self.repo.users.find(target.key).login, target.login)


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
        class MockRepo:
            def __init__(self):
                self.users = hasbug.MockUsers()
        self.repo = MockRepo()
