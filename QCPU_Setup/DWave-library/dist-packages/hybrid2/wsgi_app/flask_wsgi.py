from flask import Flask

from .base_wsgi import BaseWSGI

class FlaskWSGI(Flask, BaseWSGI):
    def __init__(self, *a, **kw):
        Flask.__init__(self, *a, **kw)
        BaseWSGI.__init__(self)

    def reflect_uri(self):
        #TODO: convert urlrule to regexp!
        return [rule.rule for rule in self.url_map.iter_rules()]

