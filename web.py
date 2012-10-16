# -*- coding: utf-8 -*-
import os
import werkzeug.serving
import hasbug.coweb, hasbug.reweb


class AppDispatcher(object):
    def _app_for(self, host):
        if host == "hasb.ug" or host == "hasbugdev:8000":
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

if __name__ == '__main__':
    werkzeug.serving.run_simple('localhost', 8000, app, use_debugger=True, use_reloader=True, passthrough_errors=True)
