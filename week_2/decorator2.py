import json
import tempfile
import os
from functools import wraps

storage_path = os.path.join(tempfile.gettempdir(), 'storage.data')


def to_json(func):
    @wraps(func)
    def to_json_wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        result = json.dumps(result)
        if result is None or result == "None":
            result = 'null'
            with open(storage_path, 'w') as json_file:
                json_file.write(json.dumps(result))
            return result
        else:
            with open(storage_path, 'w') as json_file:
                json_file.write(json.dumps(result))
            return result
    return to_json_wrapped