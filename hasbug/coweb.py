# -*- coding: utf-8 -*-
"""
coweb: An app console. Provicing per-user data access, etc.
"""

import urlparse, os
import hasbug
import functools
import flask as f
import hasbug.oauth
import hasbug.user
import hasbug.conf


template_dir = os.path.join(os.path.dirname(__file__), "templates")
app = hasbug.App(__name__, template_folder=template_dir)

app.secret_key = hasbug.conf.flask_secret_key()

def ensuring_login(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if not f.request.user:
            return f.redirect("/login")
        return fn(*args, **kwargs)
    return wrapper

@f.request_started.connect_via(app)
def restore_user_from_session(sender, **extra):
    user_key = f.session.get('user')
    f.request.user = sender.r.users.find(user_key) if user_key else None

def save_user_to_session(sess, user):
    f.session['user'] = user.key
    f.session.modified = True

def login_as_octocat(sess):
    save_user_to_session(sess, hasbug.User(hasbug.user.octocat_dict))

def set_auth_state(sess):
    state = hasbug.oauth.random_string()
    sess["auth_state"] = state
    return state

@app.route('/')
def hello_world():
    return f.render_template("index.html", user=f.request.user)

@app.route('/login')
def login_oauth():
    state = set_auth_state(f.session)
    return f.redirect(hasbug.oauth.redirect_url(state))

@app.route('/logout', methods=["POST"])
def logout():
    # FIXME: Guard against CSRF
    f.session.clear()
    return f.redirect("/")

@app.route('/login/back')
def login_callback():
    code = f.request.args["code"]
    state = f.request.args["state"]
    if f.session.get("auth_state") != state:
        return f.abort(401)
    user_dict = hasbug.oauth.authorize_user(code, state)
    user = hasbug.user.User(user_dict)
    app.r.users.add(user, can_replace=True)
    save_user_to_session(f.session, user)
    return f.redirect("/me")

@app.route('/me')
@ensuring_login
def user_home():
    return 'Hello, {user}!'.format(user=f.request.user.login)

@app.route('/~<user>')
def user_public(user):
    return 'Hello, {user}!'.format(user=user)

@app.route('/debug/login')
def debug_login():
    if not app.in_debug():
        return f.abort(401)
    login_as_octocat(f.session)
    return f.redirect("/")
