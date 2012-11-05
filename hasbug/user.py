# -*- coding: utf-8 -*-

import json
import hasbug.store as store
import hasbug.validation as validation

octocat_text = """
{
  "login": "octocat",
  "id": 1,
  "avatar_url": "https://github.com/images/error/octocat_happy.gif",
  "gravatar_id": "somehexcode",
  "url": "https://api.github.com/users/octocat",
  "name": "monalisa octocat",
  "company": "GitHub",
  "blog": "https://github.com/blog",
  "location": "San Francisco",
  "email": "octocat@github.com",
  "hireable": false,
  "bio": "There once was...",
  "public_repos": 2,
  "public_gists": 1,
  "followers": 20,
  "following": 0,
  "html_url": "https://github.com/octocat",
  "created_at": "2008-01-14T04:33:35Z",
  "type": "User"
}
"""

octocat_dict = json.loads(octocat_text)

class UserOps(object):
    pass


class Users(store.Bag, store.BagOps, UserOps):
    def __init__(self, *args, **kwargs):
        super(Users, self).__init__(*args, **kwargs)
        self.model_class = User


class MockUsers(store.MockBag, UserOps):
    def __init__(self, *args, **kwargs):
        super(MockUsers, self).__init__(*args, **kwargs)
        u = User(octocat_dict)
        self._dict[u.url] = u


class User(object):
    def __init__(self, user_dict):
        self.user_dict = user_dict

    @property
    def url(self):
        return self.user_dict["url"]        

    @property
    def key(self):
        return self.url

    @property
    def login(self):
        return self.user_dict["login"]

    @property
    def dumps(self):
        json.dumps(self.user_dict)

    def validate(self):
        v = validation.Validator(self)
        return v

    def __eq__(self, other):
        return self.user_dict == other.user_dict

    def to_item_values(self):
        return { "dumps": self.dumps }

    @classmethod
    def from_item(cls, item):
        return cls(store.Bag.from_internal_key(item.hash_key),
                   json.loads(item.get("dumps")))
