# -*- coding: utf-8 -*-

import hasbug.shortener as shortener

class Repo(object):

    shortener_repo_class = shortener.ShortenerRepo

    def __init__(self):
        pass

    @property
    def shorteners(self):
        if not getattr(self, "_shorteners", None):
            self._shorteners = self.shortener_repo_class()
        return self._shorteners
