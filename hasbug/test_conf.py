
import unittest
import hasbug.conf as conf

class ConfgTest(unittest.TestCase):
    def test_hello(self):
        self.assertEquals("bar", conf.get("Test", "foo"))
        self.assertIsNotNone(conf.github_client_id())
        self.assertIsNotNone(conf.github_client_secret())
