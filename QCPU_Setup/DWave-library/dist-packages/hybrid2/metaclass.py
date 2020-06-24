import string
import types
import traceback
import tornado

class CatchExceptionMeta(type):
    def __new__(mcs, cls_name, bases, attrs):
        supported_methods = map(string.lower, 
            tornado.web.RequestHandler.SUPPORTED_METHODS)
        for attr in attrs:
            if attr in supported_methods and \
                isinstance(attrs[attr], types.FunctionType):
                attrs[attr] = CatchExceptionMeta.catch(attrs[attr])
        return type.__new__(mcs, cls_name, bases, attrs)

    @staticmethod
    def catch(f):
        def _inner(self, *a, **kw):
            try:
                return f(self, *a, **kw)
            except Exception as _:
                self.set_status(500)
                self.write(traceback.format_exc())
                self.finish()
        return _inner 

