import json
import tempfile
import os
from functools import wraps

storage_path = os.path.join(tempfile.gettempdir(), 'storage.data')

def to_json(func):
    @wraps(func)
    def to_json_wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        with open(storage_path, 'w') as json_file:
            json_file.write(json.dumps(result))
        return result
    return to_json_wrapped

@to_json
def decorated(num_list):
    return {
        # 'data': 88
        None
    }

# print(decorated([1,2,7,9,2]))

with open(storage_path, 'r') as json_file:
    print(json_file.read())
    # print(storage_path.format(json_file.read()))

print(decorated.__name__)