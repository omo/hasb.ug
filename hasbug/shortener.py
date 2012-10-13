# -*- coding: utf-8 -*-

import hasbug.store as store

class Shorteners(store.Bag):
    def __init__(self, *args, **kwargs):
        store.Bag.__init__(self, *args, **kwargs)

    def add(self, s):
        item = self.new_item(s.host, 0, { "pattern": s.pattern, "added_by": s.added_by })
        item.put()
        item.save()

    def find(self, host):
        # FIXME: Better to wrap the exception?
        found = self.get_item(host, 0)
        ret = Shortener(found.get("hash"), found.get("pattern"), found.get("added_by"))
        ret._item = found
        return ret

    def remove(self, item):
        item._item.delete()


class MockShorteners(object):
    def __init__(self, *args, **kwargs):
        self._dict = {}
        self._dict["wkcheck.in"] = Shortener("wkcheck.in", 
                                             "http://trac.webkit.org/changeset/{id}")
        self._dict["wkb.ug"] = Shortener("wkb.ug", 
                                         "https://bugs.webkit.org/show_bug.cgi?id={id}")

    def add(self, s):
        self._dict[s.host] = s

    def find(self, host):
        return self._dict[host]

    def remove(self, item):
        del self._dict[item.host]


class Shortener(object):
    def __init__(self, host, pattern, added_by=None):
        self.host = host
        self.pattern = pattern
        self.added_by = added_by

    def url_for(self, id):
        return self.pattern.format(id = id)

    def __eq__(self, other):
        return self.host == other.host and self.pattern == other.pattern and self.added_by == self.added_by
