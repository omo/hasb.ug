# -*- coding: utf-8 -*-

import json, urllib2, StringIO
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

mojombo_text = """
{
  "type": "User",
  "avatar_url": "https://secure.gravatar.com/avatar/25c7c18223fb42a4c6ae1c8db6f50f9b?d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png",
  "url": "https://api.github.com/users/mojombo",
  "gravatar_id": "25c7c18223fb42a4c6ae1c8db6f50f9b",
  "public_gists": 66,
  "following": 11,
  "html_url": "https://github.com/mojombo",
  "email": "tom@github.com",
  "location": "San Francisco",
  "hireable": false,
  "blog": "http://tom.preston-werner.com",
  "bio": "",
  "followers": 8252,
  "company": "GitHub, Inc.",
  "login": "mojombo",
  "public_repos": 53,
  "name": "Tom Preston-Werner",
  "created_at": "2007-10-20T05:24:19Z",
  "id": 1
}
"""

mojombo_dict = json.loads(mojombo_text)

urlopen = urllib2.urlopen

fake_user_dict = {}

def fake_urlopen():
    global urlopen
    def faked(req):
        return StringIO.StringIO(fake_user_dict[req.get_full_url()])
    urlopen = faked

def add_fake_mojombo_to_urlopen():
    fake_user_dict[mojombo_dict["url"]] = mojombo_text


class User(store.Stuff):
    bag_name = "users"
    key_prop_name = "url"
    
    def __init__(self, user_dict):
        super(User, self).__init__()
        self.user_dict = user_dict

    @property
    def url(self):
        return self.user_dict["url"]      

    @property
    def login(self):
        return self.user_dict["login"]

    @property
    def name(self):
        return self.user_dict["name"]

    @property
    def dumps(self):
        return json.dumps(self.user_dict)

    def validate(self):
        v = validation.Validator(self)
        return v

    def __eq__(self, other):
        return self.user_dict == other.user_dict

    def to_item_values(self):
        return { "dumps": self.dumps }

    @classmethod
    def from_item(cls, item):
        return cls(json.loads(item.get("dumps")))

    @classmethod
    def url_from_login(cls, login):
        return "https://api.github.com/users/" + login

    @classmethod
    def remove_by_url(cls, bag, url):
        toremove = bag.find(url)
        bag.remove(toremove)

    @classmethod
    def add_by_login(cls, bag, login_name):
        url = User.url_from_login(login_name)
        opened = urlopen(urllib2.Request(url))
        toadd = User(json.load(opened))
        bag.add(toadd, can_replace=True)

    @classmethod
    def fill_mock_bag(cls, bag):
        bag.add(User(octocat_dict))
