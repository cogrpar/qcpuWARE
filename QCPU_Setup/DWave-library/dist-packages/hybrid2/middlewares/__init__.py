import re

class ChooseAPPMiddleware:
    def __init__(self, *apps):
        self._apps = apps

    def __call__(self, environment, start_response):
        d = {}
        for app in reversed(self._apps):
            d.update(dict.fromkeys(app.reflect_uri(), app))

        uri = environment['PATH_INFO']
        for uri_pattern in d:
            if re.match(uri_pattern, uri):
                return d[uri_pattern](environment, start_response)
        return self._apps[0](environment, start_response)

class DispatchMiddleWare:
    def __init__(self, app, path, argname, mapping, deny=True):
        self._app = app
        self._path = path
        self._argname = argname
        self._mapping = mapping
        self._deny = deny

    def __call__(self, environment, start_response):
        path = environment["PATH_INFO"]
        if self._deny and path in self._mapping.values():
            content = "page is not found"
            start_response("404 Not Found", [
                        ("Content-Length", str(len(content)))
                    ])
            return [content]
        if self._path == path:
            qr = environment["QUERY_STRING"]
            for one_arg in qr.split("&"):
                if not one_arg.startswith(self._argname+"="):
                    continue
                _, key = one_arg.split("=", 1)
                if key in self._mapping:
                    environment["PATH_INFO"] = self._mapping[key]
                break
        return self._app(environment, start_response)

