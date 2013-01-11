# -*- coding: utf-8 -*-

import types
import hasbug.store as store
import hasbug.validation as validation
import hasbug.user
import hasbug.shortener

OWNERSHIP_UPPER_LIMIT = 10

class Belongings(object):
    def __init__(self, ownerhips):
        self._ownerhips = ownerhips

    @property
    def shortener_hosts(self):
        return [ o.which for o in self._ownerhips if o.what == hasbug.Shortener.bag_name ]

    @property
    def has_shortener_hosts(self):
        return 0 < len(self.shortener_hosts)

    @property
    def len(self):
        return len(self.shortener_hosts)

    @property
    def reaches_upper_limit(self):
        return OWNERSHIP_UPPER_LIMIT <= self.len


class Ownership(store.Stuff):
    bag_name = "ownerships"
    attributes = [store.StuffKey("owner_key"), store.StuffAttr("what"), store.StuffOrd("which")]

    @classmethod
    def make(cls, owner_key, what, which):
        return cls({ "owner_key": owner_key, "what": what, "which": which })

    @store.storing
    @classmethod
    def add_shortener(cls, repo, shortener):
        repo.shorteners.add(shortener)
        repo.pattern_signatures.update_pattern(shortener.pattern, shortener.host)
        return repo.ownerships.add(Ownership.make(shortener.added_by, shortener.bag_name, shortener.key))

    @store.storing
    @classmethod
    def add_shortener(cls, repo, shortener):
        belongins = repo.belongings_for(shortener.added_by)
        if belongins and belongins.reaches_upper_limit:
            raise validation.raise_validation_error(
                shortener, "added_by", "The ower {owner} already has too many shorteners".format(owner=shortener.added_by_login))

        sig = repo.pattern_signatures.ensure(shortener.pattern)
        if not sig.worth_adding(shortener.pattern, shortener.host):
            covered_by = sig.hosts_for(shortener.pattern)
            raise validation.raise_validation_error(
                shortener, "pattern", "The pattern is covered by {host}".format(host=covered_by[0]))
        sig.add(shortener.pattern, shortener.host)

        # FIXME: Here is a race condition. (We can live with it though).
        repo.shorteners.add(shortener)
        repo.pattern_signatures.add(sig, can_replace=True)
        return repo.ownerships.add(Ownership.make(shortener.added_by, shortener.bag_name, shortener.key))

    @store.storing
    @classmethod
    def remove_shortener(cls, repo, shortener):
        sig = None
        try:
            sig = repo.pattern_signatures.find_by_pattern(shortener.pattern)
            sig.remove(shortener.pattern)
        except store.ItemNotFoundError:
            pass

        repo.ownerships.remove_found(shortener.added_by, shortener.key)
        if sig:
            repo.pattern_signatures.add(sig, can_replace=True)
        repo.shorteners.remove(shortener)

    @store.storing
    @classmethod
    def update_shortener(cls, repo, shortener):
        toupdate = repo.shorteners.find(shortener.host)
        # FIXME: Once we support named shorteer, this won't be able to be this naive.
        repo.remove_shortener(toupdate)
        repo.add_shortener(shortener)

    @store.storing
    @classmethod
    def belongings_for(cls, repo, owner):
        key = owner if isinstance(owner, types.StringType) or isinstance(owner, types.UnicodeType) else owner.key
        return Belongings(repo.ownerships.query(key))
