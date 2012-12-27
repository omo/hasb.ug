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

@app.route('/<string:bugid>')
def redirect(bugid):
    if not re.match("^\d+$", bugid):
        return f.make_response("Non-digit response is not allowed", 403)
    try:
        host = find_host()
        shortener = app.r.shorteners.find(host)
        return f.redirect(shortener.url_for(bugid))
    except hasbug.ItemNotFoundError, e:
        return f.abort(404)

@app.route('/noop')
def noop():
    return "<html><body>Hello</body></html>"
