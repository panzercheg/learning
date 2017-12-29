import os
import tempfile
import argparse
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', action='store', dest='key_name', help='Key for value')
    parser.add_argument('-v', '--val', action='store', dest='val_name', help='Value to store')
    options = parser.parse_args()

    key1 = options.key_name
    val1 = options.val_name

    my_dict = {}

    storage_path = os.path.join(tempfile.gettempdir(), 'storage.data')
    print(storage_path)
    if os.path.isfile(storage_path):
        with open(storage_path) as data:
            my_dict = json.load(data)

    if key1 and val1:
        if key1 in my_dict:
            my_dict[key1].append(val1)
        else:
            my_dict[key1] = [val1,]

        with open(storage_path, 'w') as data:
            data.write(json.dumps(my_dict))

        print(my_dict)

    if key1 and not val1:
        if os.path.isfile(storage_path):
            print('read ' + storage_path)
            with open(storage_path) as data:
                my_dict = json.load(data)
                print('Get value: {value} from key: {key}'.format(value=my_dict.get(key1), key=key1))


if __name__ == '__main__':
    main()