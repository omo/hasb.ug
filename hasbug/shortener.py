# -*- coding: utf-8 -*-

import hasbug.store as store
import hasbug.validation as validation
import hasbug.user as user

class Shortener(store.Stuff):
    bag_name = "shorteners"
    key_prop_name = "host"

    def __init__(self, host, pattern, added_by=None):
        super(Shortener, self).__init__()
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

    def to_item_values(self):
        return { "pattern": self.pattern, "added_by": self.added_by }

    @classmethod
    def remove_by_host(cls, bag, host):
        toremove = bag.find(host)
        bag.remove(toremove)

    @classmethod
    def from_item(cls, item):
        return cls(store.Bag._from_item_hash(item.hash_key),
                   item.get("pattern"), item.get("added_by"))

    @classmethod
    def fill_mock_bag(cls, bag):
        bag.add(Shortener(host="wkb.ug", pattern="https://bugs.webkit.org/show_bug.cgi?id={id}", added_by="https://github.com/octocat"))
        bag.add(Shortener(host="wkcheck.in", pattern="http://trac.webkit.org/changeset/{id}", added_by="https://github.com/octocat"))
