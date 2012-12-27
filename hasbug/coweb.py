# -*- coding: utf-8 -*-
"""
coweb: An app console. Provicing per-user data access, etc.
"""

import urlparse
import functools
import flask as f
import json
import re
import urllib, urllib2, urlparse
import zlib

import hasbug
import hasbug.oauth
import hasbug.user
import hasbug.conf
import hasbug.store

class BackgroundImage(object):
    def __init__(self, url, height, credit):
        self.url = url
        self.height = height
        self.credit = credit

    @property
    def inline_style(self):
        return "height: {height}px; background-image: url('{url}');".format(height=self.height, url=self.url)

    @property
    def credit_url(self):
        return self.creadit

    @property
    def credit_name(self):
        return re.match("http://www.flickr.com/photos/([^/]+)", self.credit).group(1)

index_background = BackgroundImage('http://farm4.staticflickr.com/3127/3308532489_6a1bbf61fa_b.jpg', 681, "http://www.flickr.com/photos/rnw/3308532489/")
host_backgrounds = [
    BackgroundImage('http://farm6.staticflickr.com/5230/5660512933_19572efc37_b.jpg', 768, 'http://www.flickr.com/photos/powi/5660512933/'),
    BackgroundImage('http://farm3.staticflickr.com/2522/4148872265_9ea723d1f4_b.jpg', 694, 'http://www.flickr.com/photos/stuckincustoms/'),
    BackgroundImage('http://farm1.staticflickr.com/30/48858315_4448d1286b_b.jpg', 766, 'http://www.flickr.com/photos/syldavia/48858315/'),
    BackgroundImage('http://farm1.staticflickr.com/107/263370707_6fc2d0d56d_z.jpg?zz=1', 480, 'http://www.flickr.com/photos/danorth1/263370707/'),
    BackgroundImage('http://farm4.staticflickr.com/3434/3366906291_c489ff17b2_o.jpg', 674, 'http://www.flickr.com/photos/mugley/3366906291/'),
    BackgroundImage('http://farm6.staticflickr.com/5286/5323110200_4b8e353a9e_b.jpg', 683, 'http://www.flickr.com/photos/49980618@N08/5323110200/'),
    BackgroundImage('http://farm1.staticflickr.com/41/87689672_4f7b6e4cd2_b.jpg', 683, 'http://www.flickr.com/photos/jeffd/87689672/'),
    BackgroundImage('http://farm2.staticflickr.com/1155/1314862556_bc54f9d59b_b.jpg', 768, 'http://www.flickr.com/photos/leff/1314862556/'),
    BackgroundImage('http://farm1.staticflickr.com/110/275699409_fbcdbf42e5_b.jpg', 683, 'http://www.flickr.com/photos/roboppy/275699409/'),
    BackgroundImage('http://farm1.staticflickr.com/86/275048852_77aa1a7392_b.jpg', 768, 'http://www.flickr.com/photos/moirabot/275048852/'),
    BackgroundImage('http://farm2.staticflickr.com/1353/1316145314_6e050ef82b_b.jpg', 683, 'http://www.flickr.com/photos/eole/1316145314/'),
    BackgroundImage('http://farm5.staticflickr.com/4009/4438209398_d1c8a6bc74_b.jpg', 679, 'http://www.flickr.com/photos/gaensler/4438209398/'),
    BackgroundImage('http://farm4.staticflickr.com/3160/2316473778_fe71869119_b.jpg', 768, 'http://www.flickr.com/photos/tonivc/2316473778/')
]

def choose_backgrond(host):
    return host_backgrounds[abs(zlib.adler32(host))%len(host_backgrounds)]

app = hasbug.App(__name__)

app.secret_key = hasbug.conf.flask_secret_key()

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
    return f.render_template("index.html", user=f.request.user, background=index_background)

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
        found = app.r.shorteners.find(host)
        if f.request.method == "GET":
            return f.render_template("s.html", shortener=found, background=choose_backgrond(host))
        elif f.request.method == "DELETE":
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
    background = choose_backgrond(urlparse.urlparse(shortened).hostname)
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

#
# Filters
#
@app.template_filter('link_to_profile')
def link_to_profile(s):
    return "http://github.com/{0}".format(s)

@app.template_filter('link_to_host')
def link_to_host(s):
    return "http://{0}/".format(s)

@app.template_filter('pattern_to_ellipsis')
def pattern_to_ellipsis(p):
    return p.format(id="...")

@app.template_filter('urlencode')
def urlencode_filter(s):
    return urllib.quote_plus(s)
