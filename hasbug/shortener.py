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

    def translate_error(self, exception):
        if isinstance(exception, store.ItemInvalidError):
            v = validation.Validator(self)
            return v.found_invalid("host", "{host} is already taken".format(host=self.host)).error()
        return None
            
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


class PatternSignature(store.Stuff):
    bag_name = "pattern_signatures"
    attributes = [store.StuffKey("signature"), store.StuffAttr("patterns")]

    def __init__(self, dict={}):
        super(PatternSignature, self).__init__(dict)
        if "patterns" not in self._dict:
            self._dict["patterns"] = {}

    def _shorten(self, url):
        # FIXME:
        prefix, suffix = self.pattern.split("{id}")
        id = url.replace(prefix, "").replace(suffix, "")
        if not re.match("^[a-zA-Z0-9]+$", id):
            raise ValueError("{id} is not valid id".format(id=id))
        return "http://{host}/{id}".format(host=self.host, id=id)

    def shorten(self, url):
        best = None
        for host, pattern in self.patterns.items():
            prefix, suffix = pattern.split("{id}")
            if not url.startswith(prefix) or not url.endswith(suffix):
                continue
            id = url.replace(prefix, "").replace(suffix, "")
            if not re.match("^[a-zA-Z0-9]+$", id):
                raise ValueError("{id} is not valid id".format(id=id))
            candidate = "http://{host}/{id}".format(host=host, id=id)
            if not best or len(candidate) < len(best):
                best = candidate
        if not best:
            raise ValueError("{url} cannot be shortened".format(url=url))
        return best
            
    def hosts_for(self, pattern):
        return [ h for (h, p) in self.patterns.items() if p == pattern ]

    def add(self, pattern, host):
        assert self.signature_from_pattern(pattern) == self.signature
        assert 0 == len(self.hosts_for(pattern))
        self.patterns[host] = pattern

    def remove(self, pattern):
        for h in self.hosts_for(pattern):
            self.patterns.pop(h)

    @classmethod
    def signature_from_url(cls, url):
        return re.sub("([^a-zA-Z])", "", re.sub("http(s)?://", "",  url))

    @classmethod
    def signature_from_pattern(cls, pattern):
        return cls.signature_from_url(pattern.format(id=0))

    @classmethod
    def make(cls, signature):
        return PatternSignature(dict={ "signature": signature, "patterns": {} })

    @store.bagging
    @classmethod
    def find_by_url(cls, bag, url):
        return bag.find(PatternSignature.signature_from_url(url))

    @store.bagging
    @classmethod
    def find_by_pattern(cls, bag, pattern):
        return bag.find(PatternSignature.signature_from_pattern(pattern))

    @store.bagging
    @classmethod
    def ensure(cls, bag, pattern):
        sig = PatternSignature.signature_from_pattern(pattern)
        try:
            return bag.find(sig)
        except store.ItemNotFoundError:
            return PatternSignature.make(sig)

