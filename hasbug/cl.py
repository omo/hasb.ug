# -*- coding: utf-8 -*-

import sys
import subprocess
from cement.core import backend, foundation, controller, handler, exc

import hasbug, hasbug.testing, hasbug.prod, hasbug.conf

class AppController(controller.CementBaseController):
    class Meta:
        config_defaults = {}

        arguments = [
            (['-m', '--mock'], dict(action='store_true', help='Uses mock')),
            (['-d', '--dir'], dict(action='store', help='Target directory')),
            (['--prod'], dict(action='store_true', help='Uses production database')),
            (['-n', '--host'], dict(action='store', help='Shortener Host Name (Ex: wkb.ug)')),
            (['-l', '--login'], dict(action='store', help='User Github login name (Ex: octocat)')),
            (['-p', '--pattern'], dict(action='store', help='Shortener Pattern (Ex: "https://bugs.webkit.org/show_bug.cgi?id={id}")')),
            (['-u', '--user'], dict(action='store', help='A user URL who addds the Shortener (Ex: "http://dodgson.org/omo")'))
            ]

    def _error_exit(self, message):
        self.log.error(message)
        sys.exit(1)
    
    def __init__(self, *args, **kwargs):
        super(AppController, self).__init__(*args, **kwargs)
        self.o = sys.stdout
        self.__repo = None

    def _set_repo(self, r):
        self.__repo = r

    @property
    def _repo(self):
        # FIXME: Should have a way to use a mock.
        if self.__repo:
            return self.__repo
        self.__repo = self._make_repo()
        return self.__repo

    def _make_repo(self):
        table_name = hasbug.prod.TABLE_NAME if self.pargs.prod else hasbug.testing.TABLE_NAME
        if self.pargs.mock:
            table_name = None 
        return hasbug.Repo(table_name)
        

    @controller.expose(aliases=["as"], help="Add a new shortener.")
    def add_shortener(self):
        if not self.pargs.host:
            self._error_exit("host is missing")
        if not self.pargs.pattern:
            self._error_exit("pattern is missing")
        if not self.pargs.user:
            self._error_exit("user is missing")
        toadd = hasbug.Shortener.make(self.pargs.host, self.pargs.pattern, self.pargs.user)
        self._repo.add_shortener(toadd)

    @controller.expose(aliases=["us"], help="Add a new shortener.")
    def update_shortener(self):
        if not self.pargs.host:
            self._error_exit("host is missing")
        toupdate = self._repo.shorteners.find(self.pargs.host)
        self._repo.update_shortener(toupdate)

    @controller.expose(aliases=["ls"], help="List shorteners.")
    def list_shorteners(self):
        listed = self._repo.shorteners.list()
        for i in listed:
            self.o.write("{:<10} {:<50} {:10}\n".format(i.host, i.pattern, i.added_by))
        self.o.write("total {} shorteners found.\n".format(len(listed)))

    @controller.expose(aliases=["ds"], help="Delete shorteners.")
    def delete_shortener(self):
        if not self.pargs.host:
            self._error_exit("host is missing")
        todel = self._repo.shorteners.find(self.pargs.host)
        self._repo.shorteners.remove(todel)
        self.o.write("Deleted {}.\n".format(todel.host))

    @controller.expose(aliases=["au"], help="Add a new user.")
    def add_user(self):
        if not self.pargs.login:
            self._error_exit("login is missing")
        self._repo.users.add_by_login(self.pargs.login)

    @controller.expose(aliases=["lu"], help="List users.")
    def list_users(self):
        listed = self._repo.users.list()
        for i in listed:
            self.o.write("{:<16} {:<30}\n".format(i.login, i.name))
        self.o.write("total {} users found.\n".format(len(listed)))

    def _setup_s3cmd_conf(self):
        confname = "confs/s3cmd.conf"
        conftmpl = "confs/s3cmd.conf.tmpl"
        f = open(confname, "w")
        f.write(open(conftmpl).read().format(access_key=hasbug.conf.aws_access_key_id(), 
                                             secret_key=hasbug.conf.aws_secret_access_key()))
        f.close()
        return confname
        
    @controller.expose(aliases=["upload-asset"], help="Upload asset.")
    def upload_asset(self):
        if not self.pargs.dir:
            self._error_exit("dir is missing")
        confname = self._setup_s3cmd_conf()
        args = ["s3cmd", "-c", confname, "sync", "--acl-public", self.pargs.dir, "s3://hasbug-asset/public/"]
        subprocess.call(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

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
