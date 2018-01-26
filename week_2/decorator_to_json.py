import json
import tempfile
import os
from functools import wraps

storage_path = os.path.join(tempfile.gettempdir(), 'storage.data')


def to_json(func):
    @wraps(func)
    def to_json_wrapped(*args, **kwargs):
        # result = '{}'.format(func(*args, **kwargs))
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


@to_json
def decorated(num_list):
    return num_list

decorated("")

# print(decorated([1,2,3,9,2]))
# print(decorated([""]))

with open(storage_path, 'r') as json_file:
    print("Читаем файл json " + json_file.read())
    print("форматируем файл в тру-json " + storage_path.format(json_file.read()))

print("имя декорируемой функции " + decorated.__name__)