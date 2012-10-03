# -*- coding: utf-8 -*-
"""
coweb: An app console. Provicing per-user data access, etc.
"""

import flask as f

app = f.Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello Console!'

