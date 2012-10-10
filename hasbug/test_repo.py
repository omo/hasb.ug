
import unittest
import hasbug

class MockRepoTest(unittest.TestCase):
    def test_shorteners(self):
        target = hasbug.MockRepo()
        found = target.shorteners.find("wkb.ug")
        self.assertIsInstance(found, hasbug.Shortener)
