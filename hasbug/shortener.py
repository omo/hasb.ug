# -*- coding: utf-8 -*-

import hasbug.store as store
import hasbug.validation as validation

class ShortenersOps(object):
    def remove_by_host(self, host):
        toremove = self.find(host)
        self.remove(toremove)


class Shorteners(store.Bag, store.BagOps, ShortenersOps):
    def __init__(self, *args, **kwargs):
        super(Shorteners, self).__init__(*args, **kwargs)
        self.model_class = Shortener


class MockShorteners(store.MockBag, ShortenersOps):
    def __init__(self, *args, **kwargs):
        super(MockShorteners, self).__init__(*args, **kwargs)
        self._dict["wkcheck.in"] = Shortener("wkcheck.in", 
                                             "http://trac.webkit.org/changeset/{id}")
        self._dict["wkb.ug"] = Shortener("wkb.ug", 
                                         "https://bugs.webkit.org/show_bug.cgi?id={id}")



class Shortener(object):
    def __init__(self, host, pattern, added_by=None):
        self.host = host
        self.pattern = pattern
        self.added_by = added_by

    def url_for(self, id):
        return self.pattern.format(id = id)

    @property
    def key(self):
        return self.host

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

    def to_item_values(self):
        return { "pattern": self.pattern, "added_by": self.added_by }

    @classmethod
    def from_item(cls, item):
        return cls(store.Bag.from_internal_key(item.hash_key),
                   item.get("pattern"), item.get("added_by"))

