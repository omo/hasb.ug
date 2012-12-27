# -*- coding: utf-8 -*-
"""
reweb: Redirectors and other domain based services
"""

import re
import flask as f
import logging
import hasbug

app = hasbug.App(__name__)

def find_host():
    host_may_with_port = f.request.headers.get("host")
    return re.sub("\\:\\d+$", "", host_may_with_port)
    
@app.route('/')
def index():
    host = find_host()
    return f.redirect("http://hasb.ug/s/{host}".format(host=host))

@app.route('/<int:bugid>') # FIXME: should be digits rather than a number
def redirect(bugid):
    try:
        host = find_host()
        shortener = app.r.shorteners.find(host)
        return f.redirect(shortener.url_for(bugid))
    except hasbug.ItemNotFoundError, e:
        return f.abort(404)

@app.route('/noop')
def noop():
    return "<html><body>Hello</body></html>"
