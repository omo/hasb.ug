# -*- coding: utf-8 -*-

import hasbug.store as store
import hasbug.validation as validation
import hasbug.user
import hasbug.shortener

class Ownership(store.Stuff):
    bag_name = "ownerships"
    key_prop_name = "owner_key"
    ord_prop_name = "which"
    attributes = [store.StuffAttr("owner_key"), store.StuffAttr("what"), store.StuffAttr("which")]

    @classmethod
    def make(cls, owner_key, what, which):
        return cls({ "owner_key": owner_key, "what": what, "which": which })

    @store.storing
    @classmethod
    def add_shortener(cls, repo, shortener):
        repo.shorteners.add(shortener)
        repo.ownerships.add(Ownership.make(shortener.added_by, shortener.bag_name, shortener.key))

    @store.storing
    @classmethod
    def remove_shortener(cls, repo, shortener):
        repo.ownerships.remove(repo.ownerships.find(shortener.added_by, shortener.key))
        repo.shorteners.remove(shortener)
