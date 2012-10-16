# -*- coding: utf-8 -*-
import os
import werkzeug.serving
import hasbug.coweb, hasbug.reweb


class AppDispatcher(object):
    def _app_for(self, host):
        if host == "hasb.ug":
            return hasbug.coweb.app
        else:
            return hasbug.reweb.app
        
    def __call__(self, environ, start_response):
        app = self._app_for(environ['HTTP_HOST'])
        return app(environ, start_response)


app = AppDispatcher()

if not os.environ.get("HASBUG_PROD"):
    hasbug.reweb.app.config['DEBUG'] = True
    hasbug.coweb.app.config['DEBUG'] = True
