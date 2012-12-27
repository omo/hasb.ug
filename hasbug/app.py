# -*- coding: utf-8 -*-

import os
import flask
import hasbug.repo as repo
import hasbug.prod as prod
import hasbug.session as session


template_dir = os.path.join(os.path.dirname(__file__), "templates")
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
s3_endpoint = "http://hasbug-asset.s3-website-us-east-1.amazonaws.com"

class App(flask.Flask):
    def __init__(self, *args, **kwargs):
        kwargs.update({ "template_folder": template_dir,
                        "static_folder": static_dir })
        flask.Flask.__init__(self, *args, **kwargs)
        def get_repo():
            return self.r
        self.session_interface = session.SessionInterface(get_repo)
        self._r = None
        self.jinja_env.globals["user"] = None
        self.jinja_env.globals["canary"] = None
        self.jinja_env.globals["url_for"] = self.s3_aware_url_for

    def s3_aware_url_for(self, endpoint, **values):
        if prod.in_prod and endpoint == "static":
            return s3_endpoint + flask.url_for(endpoint, **values)
        return flask.url_for(endpoint, **values)

    @property
    def r(self):
        if not self._r:
            self._r = repo.Repo(self.config['REPO_TABLE'])
        return self._r

    @r.setter
    def r(self, val):
        self._r = val

    def in_debug(self):
        return self.config['DEBUG']
