# -*- coding: utf-8 -*-

import json, urllib2, StringIO
import hasbug.store as store
import hasbug.validation as validation
import hasbug.net as net

octocat_text = """
{
  "type": "User",
  "organizations_url": "https://api.github.com/users/octocat/orgs",
  "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",
  "avatar_url": "https://secure.gravatar.com/avatar/7ad39074b0584bc555d0417ae3e7d974?d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png",
  "blog": "http://www.github.com/blog",
  "events_url": "https://api.github.com/users/octocat/events{/privacy}",
  "gravatar_id": "7ad39074b0584bc555d0417ae3e7d974",
  "followers": 276,
  "received_events_url": "https://api.github.com/users/octocat/received_events",
  "login": "octocat",
  "created_at": "2011-01-25T18:44:36Z",
  "company": "GitHub",
  "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",
  "public_repos": 3,
  "url": "https://api.github.com/users/octocat",
  "public_gists": 4,
  "html_url": "https://github.com/octocat",
  "location": "San Francisco",
  "hireable": false,
  "name": "The Octocat",
  "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",
  "bio": null,
  "followers_url": "https://api.github.com/users/octocat/followers",
  "id": 583231,
  "following": 0,
  "email": "octocat@github.com",
  "repos_url": "https://api.github.com/users/octocat/repos",
  "following_url": "https://api.github.com/users/octocat/following"
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

def add_fake_users_to_urlopen():
    net.add_fake_data(mojombo_dict["url"], mojombo_text)
    net.add_fake_data(octocat_dict["url"], octocat_text)

class User(store.Stuff):
    bag_name = "users"
    attributes = [store.StuffAttr("login"), store.StuffKey("url"), store.StuffAttr("name")]

    def __init__(self, user_dict):
        super(User, self).__init__(user_dict)

    @property
    def avatar_url(self):
        return self.get_value("avatar_url")

    @classmethod
    def url_from_login(cls, login):
        return "https://api.github.com/users/" + login

    @store.bagging
    @classmethod
    def remove_by_url(cls, bag, url):
        toremove = bag.find(url)
        bag.remove(toremove)

    @store.bagging
    @classmethod
    def add_by_login(cls, bag, login_name):
        url = User.url_from_login(login_name)
        opened = net.urlopen(urllib2.Request(url))
        toadd = User(json.load(opened))
        bag.add(toadd, can_replace=True)
        return toadd

    @classmethod
    def fill_mock_bag(cls, bag):
        bag.add(User(octocat_dict))
