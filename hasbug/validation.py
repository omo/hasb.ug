# -*- coding: utf-8 -*-

import re
import urlparse

class ValidationError(Exception):
    def __init__(self, invalids):
        super(ValidationError, self).__init__()
        self.invalids = invalids

    def __str__(self):
        return ",".join([ i.message for i in self.invalids ])


class Invalid(object):
    def __init__(self, name, message=None):
        self.name = name
        self.message = message


class Validator(object):
    def __init__(self, target):
        self._target = target
        self._invalids = []

    def invalid(self):
        return 0 < len(self._invalids)

    def found_invalid(self, name, message=None):
        self._invalids.append(Invalid(name, message))
        return self

    def _target_attr(self, name):
        return getattr(self._target, name)

    def should_match(self, name, pattern, message="%s is invalid"):
        attr = self._target_attr(name)
        if not re.search(pattern, attr):
            self.found_invalid(name, message)

    def should_be_web_url(self, name, message="%s is not a URL"):
        attr = self._target_attr(name)
        u = urlparse.urlparse(attr)
        if not ("http" == u.scheme or "https" == u.scheme) or not u.netloc or not u.path:
            self.found_invalid(name, message)

    def raise_if_invalid(self):
        if (self.invalid()):
            raise self.error()

    def error(self):
        return ValidationError(self._invalids)

def raise_validation_error(target, name, message):
    Validator(target).found_invalid(name, message).raise_if_invalid()
