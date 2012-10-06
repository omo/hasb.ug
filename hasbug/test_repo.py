
import unittest
import hasbug

class RepoCase(unittest.TestCase):
    def test_shorteners(self):
        target = hasbug.Repo()
        target.shortener_repo_class = hasbug.MockShortenerRepo
        found = target.shorteners.find("wkb.ug")
        self.assertIsInstance(found, hasbug.Shortener)
