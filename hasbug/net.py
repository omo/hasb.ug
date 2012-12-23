# -*- coding: utf-8 -*-
import urllib2
import StringIO

fake_dict = {}

def urlopen(req):
    return urllib2.urlopen(req)

def fake_urlopen():
    global urlopen
    def faked(req):
        return StringIO.StringIO(fake_dict[req.get_full_url()])
    urlopen = faked

def add_fake_data(url, data):
    fake_dict[url] = data
