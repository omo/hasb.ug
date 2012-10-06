# -*- coding: utf-8 -*-

import flask
import hasbug.repo as repo

class App(flask.Flask):
    def __init__(self, *args, **kwargs):
        flask.Flask.__init__(self, *args, **kwargs)
        self.r = None
