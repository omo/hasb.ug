# -*- coding: utf-8 -*-

import re
import hasbug.store as store
import hasbug.validation as validation
import hasbug.user as user

class Shortener(store.Stuff):
    bag_name = "shorteners"
    attributes = [store.StuffKey("host"), store.StuffAttr("pattern"), store.StuffAttr("added_by")]

    def url_for(self, id):
        return self.pattern.format(id = id)

    @property
    def host_upper(self):
        return self.host.upper()

    @property
    def pattern_zero(self):
        return self.pattern % { "id": 12345 }

    @property
    def added_by_login(self):
        m = re.search("/([^/]*)$", self.added_by)
        return m.group(1)

    def validate(self):
        v = validation.Validator(self)
        v.should_match("host_upper", "^([A-Z0-9\-]{2,63}\.)*[A-Z]{2,63}$")
        v.should_be_web_url("pattern_zero")
        v.should_match("pattern", "\{id\}")
        v.should_be_web_url("added_by")
        return v

    @store.bagging
    @classmethod
    def remove_by_host(cls, bag, host):
        toremove = bag.find(host)
        bag.remove(toremove)

    @classmethod
    def fill_mock_bag(cls, bag):
        bag.add(Shortener.make(host="wkb.ug", pattern="https://bugs.webkit.org/show_bug.cgi?id={id}", added_by="https://github.com/octocat"))
        bag.add(Shortener.make(host="wkcheck.in", pattern="http://trac.webkit.org/changeset/{id}", added_by="https://github.com/octocat"))

    @classmethod
    def make(cls, host, pattern, added_by=None):
        return cls({ "host": host, "pattern": pattern, "added_by": added_by })
