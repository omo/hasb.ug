# -*- coding: utf-8 -*-
"""
coweb: An app console. Provicing per-user data access, etc.
"""

import urlparse, os
import hasbug
import flask as f
import hasbug.oauth
import hasbug.user
import hasbug.conf

app = hasbug.App(__name__, template_folder=os.path.join(os.path.dirname(__file__), "templates"))
app.secret_key = hasbug.conf.flask_secret_key()

@f.request_started.connect_via(app)
def restore_user_from_session(sender, **extra):
    user_key = f.session.get('user')
    f.request.user = sender.r.users.find(user_key) if user_key else None

def save_use_to_session(user):
    f.session['user'] = user.key
    f.session.modified = True

@app.route('/')
def hello_world():
    return f.render_template("index.html")

@app.route('/login')
def login_oauth():
    return f.redirect(hasbug.oauth.redirect_url())

@app.route('/logout', methods=["POST"])
def logout():
    # FIXME: Guard against CSRF
    f.session.clear()
    return f.redirect("/")

@app.route('/login/back')
def login_callback():
    code = f.request.args["code"]
    state = f.request.args["state"]
    if not hasbug.oauth.auth_state_matches(state):
        return f.abort(401)
    user_dict = hasbug.oauth.authorize_user(code, state)
    user = hasbug.user.User(user_dict)
    app.r.users.add(user, can_replace=True)
    save_use_to_session(user)
    return f.redirect("/~" + user.login)

@app.route('/~<user>')
def user_home(user):
    return 'Hello, {user}!'.format(user=user)
