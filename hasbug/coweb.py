# -*- coding: utf-8 -*-
"""
coweb: An app console. Provicing per-user data access, etc.
"""

import hasbug
import flask as f

app = hasbug.App(__name__)

@app.route('/')
def hello_world():
    return 'Hello Console!'

