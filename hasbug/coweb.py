# -*- coding: utf-8 -*-
"""
coweb: An app console. Provicing per-user data access, etc.
"""

import urlparse
import functools
import flask as f
import json
import urllib, urllib2, urlparse

import hasbug
import hasbug.oauth
import hasbug.user
import hasbug.conf
import hasbug.store
import hasbug.webhelpers as webhelpers

app = hasbug.App(__name__)
webhelpers.register_helpers(app)

def ensuring_login(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if not f.request.user:
            return f.redirect("/login")
        return fn(*args, **kwargs)
    return wrapper

def find_canary(req):
    return req.values.get("canary") or req.headers.get("x-hasbug-canary")

def ensuring_canary(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if not f.request.method in ["GET", "HEAD", "OPTIONS"]:
            if not f.request.canary:
                return f.abort(401)
            if find_canary(f.request) != f.request.canary:
                return f.abort(401)
        return fn(*args, **kwargs)
    return wrapper

@f.request_started.connect_via(app)
def restore_user_from_session(sender, **extra):
    user_key = f.session.get('user')
    f.request.user = sender.r.users.find(user_key) if user_key else None
    f.request.canary = f.session.get('canary')
    app.jinja_env.globals["user"] = f.request.user
    app.jinja_env.globals["canary"] = f.request.canary

def setup_user_session(sess, user):
    f.session['user'] = user.key
    f.session['canary'] = hasbug.oauth.random_string(16)
    f.session.modified = True

def login_as_octocat(sess):
    setup_user_session(sess, hasbug.User(hasbug.user.octocat_dict))

def set_auth_state(sess):
    state = hasbug.oauth.random_string()
    sess["auth_state"] = state
    return state

@app.route('/')
def index():
    return f.render_template("index.html", user=f.request.user, background=webhelpers.index_background)

@app.route('/about')
def about():
    return f.render_template("about.html")

#
# Session
#
@app.route('/login')
def login_oauth():
    state = set_auth_state(f.session)
    return f.redirect(hasbug.oauth.redirect_url(state))

@app.route('/logout', methods=["POST"])
@ensuring_canary
def logout():
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
    setup_user_session(f.session, user)
    return f.redirect("/me")

#
# User
#
@app.route('/me')
@ensuring_login
def user_private():
    belongings = app.r.belongings_for(f.request.user)
    return f.render_template("me.html", user=f.request.user, canary=f.request.canary, belongings=belongings)

#
# Shortener
#

def make_json_response(data, status=200, headers={}):
    resp = f.make_response(json.dumps(data), status, headers)
    resp.mimetype = "application/json"
    return resp

@app.route('/s/<host>', methods=["GET", "DELETE"])
@ensuring_canary
def shortener(host):
    try:
        if f.request.method == "GET":
            return f.redirect("http://{host}/".format(host=host))
        elif f.request.method == "DELETE":
            found = app.r.shorteners.find(host)
            if found.added_by != f.request.user.url:
                return f.abort(400)
            app.r.remove_shortener(found)
            return make_json_response({})
    except hasbug.store.ItemNotFoundError:
        return f.abort(404)

@app.route('/s', methods=["POST"])
@ensuring_canary
def shortener_collection():
    if f.request.method == "POST":
        host = f.request.form.get("host")
        patt = f.request.form.get("pattern")
        sner = hasbug.Shortener.make(host, patt, f.request.user.url)
        try:
            app.r.add_shortener(sner)
            location = f.url_for("shortener", host=host)
            return make_json_response({ "location": location }, 201, headers={ "location": location })
        except hasbug.validation.ValidationError, ex:
            return make_json_response({ "name": ex.invalids[0].name, "message": ex.invalids[0].message }, 403)
        except hasbug.store.ItemInvalidError:
            app.logger.exception("shortener_collection.")
            return make_json_response({ "message": "Invalid request." }, 403)
    return make_json_response({}, 200)

#
# Shortener discovery
#
@app.route('/aka/<path:url>', methods=["GET"])
def show_shorten(url):
    shortened = hasbug.shorten(app.r, url)
    background = webhelpers.choose_backgrond(urlparse.urlparse(shortened).hostname)
    return f.render_template("aka.html", url=url, shortened=shortened, background=background)

#
# Debugging
#
@app.route('/debug/login')
def debug_login():
    if not app.in_debug():
        return f.abort(401)
    login_as_octocat(f.session)
    return f.redirect("/me")

