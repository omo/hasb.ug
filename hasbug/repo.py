# -*- coding: utf-8 -*-

import hasbug.shortener as shortener
import hasbug.store as store
import hasbug.user as user

class Repo(store.Store):
    BAG_CLASSES = [shortener.Shorteners, user.Users]

    def __init__(self, name, **kwarg):
        super(Repo, self).__init__(name=name, bag_classes=Repo.BAG_CLASSES, **kwarg)


class MockRepo(object):
    BAG_CLASSES = [shortener.MockShorteners, user.MockUsers]

    def __init__(self):
        for cls in MockRepo.BAG_CLASSES:
            name = cls.__name__.lower().replace("mock", "")
            setattr(self, name, cls())
