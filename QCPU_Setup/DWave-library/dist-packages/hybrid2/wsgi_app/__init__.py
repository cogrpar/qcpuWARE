from tornado_wsgi import TornadoWSGI
from flask_wsgi import FlaskWSGI

tornadoapp = TornadoWSGI()
flaskapp   = FlaskWSGI(__name__)

