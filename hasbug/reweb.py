# -*- coding: utf-8 -*-
"""
reweb: Redirectors and other domain based services
"""

import flask as f
import logging
import hasbug

app = hasbug.App(__name__)

@app.route('/')
def hello_world():
    return 'Hello Redirector!'

@app.route('/<int:bugid>') # FIXME: should be digits rather than a number
def redirect(bugid):
    host = f.request.headers.get("host")
    try:
        shortener = app.r.shorteners.find(host)
        return f.redirect(shortener.url_for(bugid))
    except KeyError, e:
        # TODO: handle null-host case
        # TODO: handle unknown host case
        raise e