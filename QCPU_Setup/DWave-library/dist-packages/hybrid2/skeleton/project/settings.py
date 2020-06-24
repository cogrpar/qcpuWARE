#import os
from hybrid.wsgi_app import tornadoapp
from hybrid.util import imports

#curdir = os.path.dirname(os.path.abspath(__file__))
apps = [tornadoapp]
controllers = [
    #os.path.join(curdir, 'controllers'),
]

def install_controllers():
    #to avoid circular reference
    for controller in controllers:
        imports(controller)
    from . import controllers as _

