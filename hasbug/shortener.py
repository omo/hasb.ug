# -*- coding: utf-8 -*-

import hasbug.store as store
import hasbug.validation as validation

class ShortenersOps(object):
    def remove_by_host(self, host):
        toremove = self.find(host)
        self.remove(toremove)


class Shorteners(store.Bag, ShortenersOps):
    def __init__(self, *args, **kwargs):
        store.Bag.__init__(self, *args, **kwargs)

    def add(self, s):
        s.validate().raise_if_invalid()
        self.insert_item(self.new_item(s.host, 0, { "pattern": s.pattern, "added_by": s.added_by }))

    def find(self, host):
        # FIXME: Better to wrap the exception?
        return self.to_m(self.get_item(host, 0))

    def list(self):
        # FIXME: should use generator
        return [ self.to_m(i) for i in self.list_item(0) ]

    def remove(self, item):
        item._item.delete()

    @classmethod
    def to_m(cls, item):
        ret = Shortener(cls.from_internal_key(item.hash_key), item.get("pattern"), item.get("added_by"))
        ret._item = item
        return ret


class MockShorteners(ShortenersOps):
    def __init__(self, *args, **kwargs):
        self._dict = {}
        self._dict["wkcheck.in"] = Shortener("wkcheck.in", 
                                             "http://trac.webkit.org/changeset/{id}")
        self._dict["wkb.ug"] = Shortener("wkb.ug", 
                                         "https://bugs.webkit.org/show_bug.cgi?id={id}")

    def add(self, s):
        s.validate().raise_if_invalid()
        if self._dict.has_key(s.host):
            raise store.ItemInvalidError("{} is duplicated".format(s.host))
        self._dict[s.host] = s

    def find(self, host):
        try:
            return self._dict[host]
        except KeyError, ex:
            raise store.ItemNotFoundError(str(ex))

    def remove(self, item):
        del self._dict[item.host]

    def list(self):
        return self._dict.values()


class Shortener(object):
    def __init__(self, host, pattern, added_by=None):
        self.host = host
        self.pattern = pattern
        self.added_by = added_by

    def url_for(self, id):
        return self.pattern.format(id = id)

    @property
    def host_upper(self):
        return self.host.upper()

    @property
    def pattern_zero(self):
        return self.pattern % { "id": 12345 }

    def validate(self):
        v = validation.Validator(self)
        v.should_match("host_upper", "^([A-Z0-9\-]{2,63}\.)*[A-Z]{2,63}$")
        v.should_be_web_url("pattern_zero")
        v.should_match("pattern", "\{id\}")
        v.should_be_web_url("added_by")
        return v

    def __eq__(self, other):
        return self.host == other.host and self.pattern == other.pattern and self.added_by == self.added_by
