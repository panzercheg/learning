import os
import tempfile
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', action='store', dest='key_name', help='Key for value')
    parser.add_argument('-v', '--val', action='store', dest='val_name', help='Value to store')
    options = parser.parse_args()

    dict = {}
    # options.key_name = key
    # options.val_name = val

    print(tempfile.gettempdir())
    file_json = tempfile.NamedTemporaryFile
    # storage_path = os.path.join(tempfile.gettempdir(), 'storage.json')
    with open(tempfile.gettempdir(), 'r+', encoding="utf-8") as file:
        json.dump(dict, file)

    if options.key_name and options.val_name:
        dict.fromkeys([options.key_name],options.val_name)
        print('Store value in storage by key:{key1} and value:{val1}'.format(key1=options.key_name,val1=options.val_name))

    if options.key_name and not options.val_name:
        print(dict.get(options.key_name))
        print('Get key _ {key1} _ from storage '.format(key1=options.key_name))


if __name__ == '__main__':
    main()