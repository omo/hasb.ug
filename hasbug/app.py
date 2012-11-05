# -*- coding: utf-8 -*-

import flask
import hasbug.repo as repo
import hasbug.prod as prod

class App(flask.Flask):
    def __init__(self, *args, **kwargs):
        flask.Flask.__init__(self, *args, **kwargs)
        self._r = None

    @property
    def r(self):
        if not self._r:
            # Currently we have no way to conect test database.0
            self._r = repo.Repo(prod.TABLE_NAME)
        return self._r

    @r.setter
    def r(self, val):
        self._r = val

    def in_debug(self):
        return self.config['DEBUG']
