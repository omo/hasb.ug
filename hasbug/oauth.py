# -*- coding: utf-8 -*-

import random, string, urllib2, json
import hasbug.conf

# http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
def random_string(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(n))

# FIXME: Should be constantly changing
auth_state_value = random_string(6)

def auth_state():
    return auth_state_value

def auth_state_matches(given_state):
    return auth_state_value == given_state

def redirect_url():
    params = { "client_id": hasbug.conf.github_client_id(), 
               "state": auth_state() }
    return "https://github.com/login/oauth/authorize?client_id={client_id}&state={state}".format(**params)

def urlopen(req):
    return urllib2.urlopen(req)

def authorize_user(code, state):
    url = "https://github.com/login/oauth/access_token"
    data = "client_id={id}&client_secret={secret}&code={code}&state={state}".format(
        id = hasbug.conf.github_client_id(),
        secret = hasbug.conf.github_client_secret(),
        code = code,
        state = auth_state())
    req = urllib2.Request(url, data)
    req.add_header("Accept", "application/json")
    res = urlopen(req)
    resdict = json.load(res)
    token = resdict["access_token"]
        
    url = "https://api.github.com/user?access_token={token}".format(token=token)
    res = urlopen(urllib2.Request(url))
    return json.load(res)
