# -*- coding: utf-8 -*-
"""
reweb: Redirectors and other domain based services
"""

import flask as f

app = f.Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello Redirector!'

@app.route('/<int:bugid>')
def redirect(bugid):
    url = "http://trac.webkit.org/changeset/%d" % (bugid)
    return f.redirect(url)
