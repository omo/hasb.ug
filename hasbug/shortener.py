# -*- coding: utf-8 -*-

class ShortenerRepo(object):
    pass

class MockShortenerRepo(object):
    def __init__(self):
        self._dict = {}
        self._dict["wkcheck.in"] = Shortener("wkcheck.in", 
                                             "http://trac.webkit.org/changeset/{id}")
        self._dict["wkb.ug"] = Shortener("wkb.ug", 
                                         "https://bugs.webkit.org/show_bug.cgi?id={id}")

    def find(self, host):
        return self._dict[host]

class Shortener(object):

    def __init__(self, host, pattern):
        self.host = host
        self.pattern = pattern

    def url_for(self, id):
        return self.pattern.format(id = id)
