from ..settings import tornadoapp
from .base_handler import BaseHandler

@tornadoapp.route("/tornado")
class TornadoHandler(BaseHandler):
    def get(self):
        self.render_func({"uri": self.request.uri,
            "datetime": __import__("datetime").datetime.now()})

