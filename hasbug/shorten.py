# -*- coding: utf-8 -*-
import urllib2
import json

import hasbug.store as store
import hasbug.net as net

# FIXME: This result should be stored to be idemponent.
def shorten_using_googl(url):
    req = urllib2.Request("https://www.googleapis.com/urlshortener/v1/url",
                          data = json.dumps({ "longUrl": url }),
                          headers = { "Content-Type": "application/json" })
    res = net.urlopen(req)
    obj = json.load(res)
    return obj["id"]

def shorten(repo, url):
    try:
        sig = repo.pattern_signatures.find_by_url(url)
        return sig.shorten(url)
    except store.ItemNotFoundError:
        return shorten_using_googl(url)
