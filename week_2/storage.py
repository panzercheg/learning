import os
import tempfile
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', action='store', dest='key_name', help='Key for value')
    parser.add_argument('-v', '--val', action='store', dest='val_name', help='Value to store')
    options = parser.parse_args()


    storage_path = os.path.join(tempfile.gettempdir(), 'storage.data')
    print(storage_path)
    with open(storage_path, 'w+') as file_storage:
        if options.key_name and options.val_name:
            my_dict = dict.fromkeys([options.key_name], options.val_name)
            file_storage.write(json.dumps(my_dict))
            print('Store value in storage by key:{key1} and value:{val1}'.format(key1=options.key_name,
                                                                                 val1=options.val_name))

        if options.key_name and not options.val_name:
            print(file_storage.read())
            my_dict = json.loads(file_storage.read())
            print(my_dict.get(options.key_name))
            print('Get key _ {key1} _ from storage '.format(key1=options.key_name))

if __name__ == '__main__':
    main()