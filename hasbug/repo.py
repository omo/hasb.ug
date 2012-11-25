# -*- coding: utf-8 -*-

import hasbug.shortener as shortener
import hasbug.store as store
import hasbug.user as user
import hasbug.ownership as ownership

class Repo(store.Store):
    MODEL_CLASSES = [shortener.Shortener, user.User, ownership.Ownership]

    def __init__(self, name, **kwarg):
        super(Repo, self).__init__(name=name, model_classes=Repo.MODEL_CLASSES, **kwarg)
