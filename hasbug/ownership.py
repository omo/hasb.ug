# -*- coding: utf-8 -*-

import hasbug.store as store
import hasbug.validation as validation
import hasbug.user
import hasbug.shortener

class Belongings(object):
    def __init__(self, ownerhips):
        self._ownerhips = ownerhips

    @property
    def shortener_hosts(self):
        return [ o.which for o in self._ownerhips if o.what == hasbug.Shortener.bag_name ]

    @property
    def has_shortener_hosts(self):
        return 0 < len(self.shortener_hosts)

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
        return repo.ownerships.add(Ownership.make(shortener.added_by, shortener.bag_name, shortener.key))

    @store.storing
    @classmethod
    def remove_shortener(cls, repo, shortener):
        repo.ownerships.remove(repo.ownerships.find(shortener.added_by, shortener.key))
        repo.shorteners.remove(shortener)

    @store.storing
    @classmethod
    def belongings_for(cls, repo, owner):
        return Belongings(repo.ownerships.query(owner.key))
        
