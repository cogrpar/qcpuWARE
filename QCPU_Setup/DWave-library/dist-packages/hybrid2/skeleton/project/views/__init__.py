import json
import datetime

def __json_default(obj):
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%F %T')
    elif isinstance(obj, datetime.date):
        return obj.strftime('%F')
    elif isinstance(obj, datetime.time):
        return obj.strftime('%T')
    raise TypeError("%r is not JSON serializable" % obj)

def json_view(data, *a, **kw):
    return json.dumps(data, 
            default=kw.pop('default', __json_default), 
            *a, **kw)

if __name__ == "__main__":
    print json_view({'datetime': datetime.datetime.now(),
                        'date': datetime.date.today()}, indent=2)

