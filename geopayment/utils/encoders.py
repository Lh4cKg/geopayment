import json
import datetime
from decimal import Decimal

try:
    import ujson
except ImportError:
    pass


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, Decimal):
            return str(o)

        return super().default(o)


class UJSONEncoder(JSONEncoder):

    def default(self, o):
        try:
            return ujson.dumps(o)
        except TypeError:
            pass
        except NameError:
            raise ModuleNotFoundError(
                'The `ujson` is not installed. Install it using '
                '`pip install ujson`. Then, use the `UJSONEncoder` within code.'
            )
        return JSONEncoder.default(self, o)
