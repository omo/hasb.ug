# -*- coding: utf-8 -*-

import random, string
import hasbug.conf

# http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
def random_string(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(n))

# FIXME: Should be constantly changing
auth_state_value = random_string(6)

def auth_state():
    return auth_state_value

def redirect_url():
    params = { "client_id": hasbug.conf.github_client_id(), 
               "state": auth_state() }
    return "https://github.com/login/oauth/authorize?client_id={client_id}&state={state}".format(**params)
