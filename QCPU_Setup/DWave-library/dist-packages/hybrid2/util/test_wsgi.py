import urllib
import tempfile
import urlparse

class TestWSGIApplication:
    HTTP_METHODS = ('GET', 'HEAD', 'POST', 'DELETE', 'PATCH', 'PUT', 'OPTIONS')
    def __init__(self, app, server_name=None):
        self._app = app
        self._chunks = [] #storing data written by ``write``
        self._env = {} #storing WSGI environment variables
        self._env['SERVER_NAME'] = server_name or ''
        self.initialize()

    def initialize(self):
        self._env['SERVER_PROTOCOL'] = 'HTTP/1.1'
        self._env['wsgi.version'] = (1, 0)
        self._env['wsgi.input'] = tempfile.NamedTemporaryFile()
        self._env['wsgi.errors'] = tempfile.NamedTemporaryFile()
        self._env['wsgi.multithread'] = False
        self._env['wsgi.multiprocess'] = False
        self._env['wsgi.run_once'] = False

    def start_response(self, status, headers, exc_info=None):
        if not headers:
            raise RuntimeError('MissingResponseHeaders')
        self._status = status
        self.status_code = int(status.split()[0])
        self.headers = dict(headers)
        self.exc_info = exc_info
        return self.write

    def write(self, chunk):
        self._chunks.append(chunk)

    def _wrap(self, url, headers={}, params={}, data=''):
        url = urlparse.urlparse(url)
        if not url.scheme:
            raise RuntimeError('MissingSchema')
        self._env['wsgi.url_scheme'] = url.scheme
        self._env['PATH_INFO'] = url.path
        self._env['QUERY_STRING'] = urllib.urlencode(params)
        if not self._env['QUERY_STRING']:
            self._env['QUERY_STRING'] = url.query
        else:
            self._env['QUERY_STRING'] += ('' if not url.query else ('&'+url.query))
        self._env['wsgi.input'].write(data)
        self._env['wsgi.input'].seek(0)
        self._env['CONTENT_LENGTH'] = len(data)

        if headers:
            for k, v in headers.items():
                self._env['HTTP_'+k.replace('-', '_').upper()] = v
        self.response = self.finalize()
        return self

    def __str__(self):
        return self.response

    def __getattr__(self, attr):
        if not attr.upper() in self.HTTP_METHODS:
            raise AttributeError('instance of %r has no attribute: %s.'
                    % (self.__class__, attr))
        self._env['REQUEST_METHOD'] = attr.upper()
        return self._wrap

    def finalize(self):
        gen = list(self._app(self._env, self.start_response))
        self.body = ''.join(self._chunks) + ''.join(gen)

        return \
            '%s '%self._env['SERVER_PROTOCOL'] + self._status + '\r\n' + \
            "\r\n".join(['%s: %s' % (k, v) for k, v in self.headers.items()]) + \
            "\r\n\r\n" + \
            self.body

