# -*- coding: utf-8 -*-

import werkzeug.serving
import hasbug.coweb, hasbug.reweb, hasbug.prod, hasbug.testing

force_debug = False

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

def set_config(key, val):
    hasbug.reweb.app.config[key] = hasbug.coweb.app.config[key] = val

if __name__ == '__main__':
    set_config('DEBUG', not hasbug.prod.in_prod or force_debug)
    set_config('REPO_TABLE', hasbug.prod.TABLE_NAME if hasbug.prod.in_prod else hasbug.testing.TABLE_NAME)
    werkzeug.serving.run_simple('localhost', 8000, app, use_debugger=True, use_reloader=True, passthrough_errors=True)
