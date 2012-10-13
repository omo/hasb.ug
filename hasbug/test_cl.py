
import unittest
import cement.utils.test
import hasbug
import hasbug.testing as testing
import hasbug.cl


class ClTest(cement.utils.test.CementTestCase):
    app_class = hasbug.cl.App

    def setUp(self):
        super(ClTest, self).setUp()
        self.reset_backend()

    def _run(self, argv):
        app = self.make_app(argv=argv)
        app.setup()
        app.run()
        app.close()

    def test_as_mock(self):
        self._run(['as', "--mock",
                   '--host', "testhost", 
                   "--pattern", "http://test.example.com/{id}",
                   "--user", "alice"])

    @unittest.skipIf(not testing.enable_database, "Database test is disabled")
    def test_noop(self):
        self._run(['noop'])

    @unittest.skipIf(not testing.enable_database, "Database test is disabled")
    def test_noop_prod(self):
        self._run(['noop', '--prod'])

    def test_noop_mock(self):
        self._run(['noop', '--mock'])
