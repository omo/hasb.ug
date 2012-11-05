# -*- coding: utf-8 -*-
"""
coweb: An app console. Provicing per-user data access, etc.
"""

import urlparse
import hasbug
import flask as f
import hasbug.oauth
import hasbug.user
import hasbug.conf

app = hasbug.App(__name__)
app.secret_key = hasbug.conf.flask_secret_key()


@app.route('/')
def hello_world():
    return 'Hello Console!'

@app.route('/login/ask')
def login_oauth():
    return f.redirect(hasbug.oauth.redirect_url())

@app.route('/login/back')
def login_callback():
    code = f.request.args["code"]
    state = f.request.args["state"]
    if not hasbug.oauth.auth_state_matches(state):
        return f.abort(401)
    user_dict = hasbug.oauth.authorize_user(code, state)
    user = hasbug.user.User(user_dict)
    app.r.users.add(user, can_replace=True)

    f.session['user'] = user.key
    f.session.modified = True

    return f.redirect("/~" + user.login)

@app.route('/~<user>')
def user_home(user):
    return 'Hello, {user}!'.format(user=user)
