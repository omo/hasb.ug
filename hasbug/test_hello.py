
import unittest
import hasbug

class ShortenerTest(unittest.TestCase):
    def test_hello(self):
        self.repo = hasbug.MockShortenerRepo()
        target = self.repo.find("wkb.ug")
        self.assertEquals("https://bugs.webkit.org/show_bug.cgi?id=12345", 
                          target.url_for(12345))
