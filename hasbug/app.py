# -*- coding: utf-8 -*-

import os
import os.path
import re
import threading
import hashlib
import flask
import hasbug.repo as repo
import hasbug.prod as prod
import hasbug.session as session


template_dir = os.path.join(os.path.dirname(__file__), "templates")
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
s3_endpoint = "http://hasbug-asset.s3-website-us-east-1.amazonaws.com"

class StaticFilePath(object):
    
    def __init__(self, static_folder):
        self._static_folder = static_folder
        self._modifiers_local = threading.local()

    def compute_modifiers(self):
        mods = {}
        base = self._static_folder + "/"
        for root, dirnames, filenames in os.walk(self._static_folder):
            for name in filenames:
                abspath = "/".join([root, name])
                relpath = abspath.replace(base, "")
                with open(abspath) as f:
                    h = hashlib.md5()
                    h.update(f.read())
                    mods[relpath] = ".".join([h.hexdigest(), "hash"])
        return mods

    def _prefix_of(self, original_filename):
        if not hasattr(self._modifiers_local, 'value'):
            self._modifiers_local.value = self.compute_modifiers()
        return self._modifiers_local.value.get(original_filename, "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.hash")

    def to_modified_filename(self, original_filename):
        return "/".join([self._prefix_of(original_filename), original_filename])

    def to_original_filename(self, modified_filename):
        return re.sub("^[0-9a-z]+\.hash/", "", modified_filename)


class App(flask.Flask):
    def __init__(self, *args, **kwargs):
        kwargs.update({ "template_folder": template_dir,
                        "static_folder": static_dir })
        flask.Flask.__init__(self, *args, **kwargs)
        def get_repo():
            return self.r
        self.session_interface = session.SessionInterface(get_repo)
        self._static_file_path = StaticFilePath(static_dir)
        self._static_file_path.compute_modifiers()
        self._r = None
        self.jinja_env.globals["user"] = None
        self.jinja_env.globals["canary"] = None
        self.jinja_env.globals["url_for"] = self.s3_aware_url_for

    def s3_aware_url_for(self, endpoint, **values):
        if endpoint == "static":
            values['filename'] = self._static_file_path.to_modified_filename(values['filename'])
            if prod.in_prod:
                return s3_endpoint + flask.url_for(endpoint, **values)
        return flask.url_for(endpoint, **values)

    def send_static_file(self, filename):
        return super(App, self).send_static_file(self._static_file_path.to_original_filename(filename))

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

fake_modifiers = {}

def fake_static_file_computation():
    def fake(self):
        return fake_modifiers
    StaticFilePath.compute_modifiers = fake
