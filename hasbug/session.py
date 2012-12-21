# -*- coding: utf-8 -*-
# Based on http://flask.pocoo.org/snippets/75/

import hasbug.store as store

import json
from datetime import timedelta
from uuid import uuid4
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin

class Session(store.Stuff):
    bag_name = "sessions"
    attributes = [store.StuffKey("sid"), store.StuffAttr("pickle")]


class SessionObject(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class SessionInterface(SessionInterface):
    serializer = json
    session_class = SessionObject

    def __init__(self, get_store):
        self.get_store = get_store

    def generate_sid(self):
        return "sid:" + str(uuid4())

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            return self.session_class(sid=self.generate_sid(), new=True)
        try:
            found = self.get_store().sessions.find(sid)
            data = self.serializer.loads(found.pickle)
            return self.session_class(initial=data, sid=sid)
        except store.ItemNotFoundError:
            return self.session_class(sid=self.generate_sid(), new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            self.get_store().sessions.remove_found(session.sid)
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain)
            return
        cookie_exp = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.serializer.loads(val)
        self.get_store().sessions.add(Session(dict={ "sid": session.sid, "pickle": val }), can_replace=True)
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True,
                            domain=domain)
