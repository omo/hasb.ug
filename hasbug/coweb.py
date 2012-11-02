# -*- coding: utf-8 -*-
"""
coweb: An app console. Provicing per-user data access, etc.
"""

import urlparse
import hasbug
import hasbug.oauth
import flask as f

app = hasbug.App(__name__)


@app.route('/')
def hello_world():
    return 'Hello Console!'

@app.route('/login/ask')
def login_oauth():
    return f.redirect(hasbug.oauth.redirect_url())

@app.route('/login/back')
def login_callback():
    pass
