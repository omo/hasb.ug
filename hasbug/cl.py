# -*- coding: utf-8 -*-

import sys
from cement.core import backend, foundation, controller, handler, exc

import hasbug, hasbug.testing


class AppController(controller.CementBaseController):
    class Meta:
        config_defaults = {}

        arguments = [
            (['-m', '--mock'], dict(action='store_true', help='Use mock')),
            (['-n', '--host'], dict(action='store', help='Shortener Host Name (Ex: wkb.ug)')),
            (['-p', '--pattern'], dict(action='store', help='Shortener Pattern (Ex: "https://bugs.webkit.org/show_bug.cgi?id={id}")')),
            (['-u', '--user'], dict(action='store', help='A user URL who addds the Shortener (Ex: "http://dodgson.org/omo")'))
            ]

    def _error_exit(self, message):
        self.log.error(message)
        sys.exit(1)
    
    def __init__(self, *args, **kwargs):
        super(AppController, self).__init__(*args, **kwargs)
        self.table_name = hasbug.testing.TABLE_NAME # FIXME: Should have a way to point prod.

    @property
    def _repo(self):
        # FIXME: Should have a way to use a mock.
        repo = getattr(self, "__repo", None)
        if repo:
            return repo
        self.__repo = self._make_repo()
        return self.__repo

    def _make_repo(self):
        if self.pargs.mock:
            return hasbug.MockRepo()
        else:
            return hasbug.Repo(self.table_name)

    @controller.expose(aliases=["as"], help="Add a new shortener.")
    def add_shortener(self):
        if not self.pargs.host:
            self._error_exit("host is missing")
        if not self.pargs.pattern:
            self._error_exit("pattern is missing")
        if not self.pargs.user:
            self._error_exit("user is missing")
        toadd = hasbug.Shortener(self.pargs.host, self.pargs.pattern, self.pargs.user)
        self._repo.shorteners.add(toadd)

    @controller.expose(aliases=["noop"], help="Do nothing.")
    def do_nothing(self):
        self._repo # To instantiate Repo explicitly.

class App(foundation.CementApp):
    class Meta:
        label = 'hasbuger'
        base_controller = AppController


def run(args):
    app = App()
    try:
        app.setup()
        app.run()
    finally:
        app.close()