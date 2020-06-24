from hybrid.middlewares import ChooseAPPMiddleware
from .settings import apps, install_controllers
install_controllers()

application = ChooseAPPMiddleware(*apps)

