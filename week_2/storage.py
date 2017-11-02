import os
import tempfile
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', action='store', dest='key_name', help='Key for value')
    parser.add_argument('-v', '--val', action='store', dest='val_name', help='Value to store')
    options = parser.parse_args()

    if options.key_name and options.val_name:
        print('Store value in storage by key:{key1} and value:{val1}'.format(key1=options.key_name,val1=options.val_name))

    if options.key_name and not options.val_name:
        print('Get key _ {key1} _ from storage '.format(key1=options.key_name))


if __name__ == '__main__':
    main()