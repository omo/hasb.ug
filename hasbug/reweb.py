# -*- coding: utf-8 -*-
"""
reweb: Redirectors and other domain based services
"""

import re
import flask as f
import logging
import hasbug
import webhelpers
import hasbug.coweb

app = hasbug.App(__name__)
webhelpers.register_helpers(app)

def coweb_url_for(*args, **kwargs):
    with hasbug.coweb.app.test_request_context("/"):
        maybe_relative = f.url_for(*args, **kwargs)
        if maybe_relative.startswith("/"):
            return "http://hasb.ug" + maybe_relative
        return maybe_relative
app.jinja_env.globals["url_for"] = coweb_url_for

def find_host():
    host_may_with_port = f.request.headers.get("host")
    return re.sub("\\:\\d+$", "", host_may_with_port)
    
@app.route('/')
def index():
    host = find_host()
    tener = app.r.shorteners.find(host)
    return f.render_template("s.html",
                             shortener=tener,
                             background=webhelpers.choose_backgrond(host))

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
