import types
import re

from DBUtils import PooledDB

class InterfaceError(StandardError):
    pass

class db_pool(object):
    def __init__(self, db_api, **kwargs):
        if type(db_api) == types.ModuleType:
            self._db_api = db_api
        elif isinstance(db_api, basestring):
            self._db_api = __import__(db_api)
        else:
            raise InterfaceError(
                'db_api should be a module '
                'or basestring object, not %s.' % type(db_api).__name__)

        self._kwargs = kwargs
        self.mincached = self._kwargs.pop('mincached', 1)
        self.maxcached = self._kwargs.pop('maxcached', 10)
        self.maxshared = self._kwargs.pop('maxshared', 5)
        self.maxconnections = self._kwargs.pop('maxconnections', 0)
        self.blocking = self._kwargs.pop('blocking', True)
        self.ping = self._kwargs.pop('ping', 0)

        self._pool = None

    def create_pool(self):
        if self._pool is None:
            self._pool = PooledDB.PooledDB(self._db_api,
                                            self.mincached,
                                            self.maxcached,
                                            self.maxshared,
                                            self.maxconnections,
                                            self.blocking,
                                            self.ping,
                                            **self._kwargs)

    def get_conn(self):
        if self._pool is None:
            self.create_pool()
        return self._pool.connection()

    def close(self):
        if hasattr(self._pool, 'close') and callable(self._pool.close):
            self._pool.close()
        self._pool = None

    def __del__(self):
        self.close()

class db(object):
    def __init__(self, pool):
        assert isinstance(pool, db_pool)
        self._pool = pool

    def __del__(self):
        self._pool.close()

    def _create(self):
        conn = self._pool.get_conn()
        cursor = conn.cursor()
        return conn, cursor

    def _close(self, conn=None, cursor=None):
        if cursor and hasattr(cursor, 'close') and callable(cursor.close):
            cursor.close()
        if conn and hasattr(conn, 'close') and callable(conn.close):
            conn.close()

    def _commit(self, conn):
        if hasattr(conn, 'commit') and callable(conn.commit):
            conn.commit()

    def query(self, table, fields, where=' 1 = 1'):
        if not isinstance(fields, (list, tuple)):
            fields = [fields]
        sql = 'SELECT %s FROM %s WHERE %s' % (','.join(fields), table, where)

        conn, cursor = self._create() 
        cursor.execute(sql)
        for row in cursor:
            yield dict(zip(fields, row))
        self._close(conn, cursor)

    def execute(self, sql, args=None, commit=True, lastrowid=False):
        try:
            conn, cursor = self._create()
            result = cursor.execute(sql, args)
            if commit:
                self._commit(conn)
            return result if not lastrowid else cursor.lastrowid
        finally:
            self._close(conn,cursor)

    def update(self, table, row, where, escape=True):
        arr = []
        for col, val in row.iteritems():
            if isinstance(val, basestring):
                if escape: 
                    val = self.escape_string(val)
                arr.append("%s = '%s'" % (col, val))
            else:
                arr.append("%s = %s" % (col, val if val is not None else 'null'))
        sql = "UPDATE %s SET %s WHERE %s" % (table, ' , '.join(arr), where)
        return self.execute(sql)

    def escape_string(self, s):
        ESCAPE_REGEX = re.compile(r"[\0\n\r\032\'\"\\]")
        ESCAPE_MAP = {'\0':'\\0', '\n':'\\n', '\r':'\\r', '\032':'\\Z',
                        '\'':'\\\'', '"':'\\"', '\\':'\\\\'}
        return ("%s" % ESCAPE_REGEX.sub(
                lambda match: ESCAPE_MAP.get(match.group(0)), s))

    def query_one(self, *args, **kwargs):
        rs = self.query(*args, **kwargs)
        if not rs: return rs
        for r in rs:
            return r

    def insert(self, table, fields, escape=True, update=''):
        items = map(lambda t:(t[0], (self.escape_string(t[1])
            if isinstance(t[1], basestring) and escape else t[1])), fields.items())
        sql = 'INSERT INTO %s SET ' % table + ','.join(map(lambda t:'%s=%s' % (t[0], 
                'null' if t[1] is None else "'%s'"%t[1]), items)) + ' ' + update
        return self.execute(sql, lastrowid=True)

