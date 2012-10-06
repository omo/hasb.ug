# -*- coding: utf-8 -*-
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

if __name__ == '__main__':
    werkzeug.serving.run_simple('localhost', 5000, app, use_reloader=True)
