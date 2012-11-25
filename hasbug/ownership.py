# -*- coding: utf-8 -*-

import hasbug.store as store
import hasbug.validation as validation
import hasbug.user
import hasbug.shortener

class Ownership(store.Stuff):
    bag_name = "ownerships"
    key_prop_name = "owner_key"
    ord_prop_name = "which"

    def __init__(self, owner_key, what, which):
        super(Ownership, self).__init__()
        self.owner_key = owner_key
        self.what = what
        self.which = which

    def validate(self):
        v = validation.Validator(self)
        return v

    def to_item_values(self):
        return { "what": self.what, "which": self.which }

    @classmethod
    def from_item(cls, item):
        return cls(item.hash_key, item.get("what"), item.range_key)
    
    @classmethod
    def add_shortener(cls, repo, shortener):
        repo.shorteners.add(shortener)
        repo.ownerships.add(Ownership(shortener.added_by, shortener.bag_name, shortener.key))
    
    @classmethod
    def remove_shortener(cls, repo, shortener):
        repo.ownerships.remove(repo.ownerships.find(shortener.added_by, shortener.key))
        repo.shorteners.remove(shortener)


    @classmethod
    def fill_mock_bag(cls, bag):
        pass
