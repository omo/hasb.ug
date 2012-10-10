# -*- coding: utf-8 -*-

import hasbug.shortener as shortener
import hasbug.store as store

class Repo(store.Store):
    BAG_CLASSES = [shortener.Shorteners]

    def __init__(self, name, **kwarg):
        store.Store.__init__(self, name=name, bag_classes=Repo.BAG_CLASSES, **kwarg)


class MockRepo(object):
    BAG_CLASSES = [shortener.MockShorteners]

    def __init__(self):
        for cls in MockRepo.BAG_CLASSES:
            name = cls.__name__.lower().replace("mock", "")
            setattr(self, name, cls())
