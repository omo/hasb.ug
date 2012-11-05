
import StringIO
import unittest
import cement.utils.test
import hasbug
import hasbug.user
import hasbug.testing as testing
import hasbug.cl


class ClTest(cement.utils.test.CementTestCase):
    app_class = hasbug.cl.App

    def setUp(self):
        super(ClTest, self).setUp()
        self.reset_backend()
        self.faked_io = StringIO.StringIO()

    def _run(self, argv):
        app = self.make_app(argv=argv)
        app.setup()
        app.controller.o = self.faked_io
        app.run()
        app.close()

    def test_as_mock(self):
        self._run(['as', "--mock",
                   '--host', "example.com", 
                   "--pattern", "http://test.example.com/{id}",
                   "--user", "http://alice.example.com/"])

    @unittest.skipIf(not testing.enable_database, "Database test is disabled")
    def test_noop(self):
        self._run(['noop'])

    @unittest.skipIf(not testing.enable_database, "Database test is disabled")
    def test_noop_prod(self):
        self._run(['noop', '--prod'])

    def test_noop_mock(self):
        self._run(['noop', '--mock'])

    def test_list_mock(self):
        self._run(['ls', '--mock'])

    def test_au_mock(self):
        hasbug.user.fake_urlopen()
        hasbug.user.add_fake_mojombo_to_urlopen()
        self._run(['au', '--mock', '--login', 'mojombo'])

    def test_lu_mock(self):
        self._run(['lu', '--mock'])

    def test_ds_mock(self):
        self._run(['ds', '--mock', '--host', 'wkb.ug'])
        self.assertRegexpMatches(self.faked_io.getvalue(), "Deleted")
