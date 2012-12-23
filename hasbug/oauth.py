# -*- coding: utf-8 -*-

import random, string, urllib2, json, datetime
import hasbug.conf
import hasbug.net as net

# http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
def random_string(n=8):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(n))

def redirect_url(state):
    params = { "client_id": hasbug.conf.github_client_id(), 
               "state": state }
    return "https://github.com/login/oauth/authorize?client_id={client_id}&state={state}".format(**params)

def authorize_user(code, state):
    url = "https://github.com/login/oauth/access_token"
    data = "client_id={id}&client_secret={secret}&code={code}&state={state}".format(
        id = hasbug.conf.github_client_id(),
        secret = hasbug.conf.github_client_secret(),
        code = code,
        state = state)
    req = urllib2.Request(url, data)
    req.add_header("Accept", "application/json")
    res = net.urlopen(req)
    resdict = json.load(res)
    token = resdict["access_token"]
    url = "https://api.github.com/user?access_token={token}".format(token=token)
    res = net.urlopen(urllib2.Request(url))
    return json.load(res)
