import os
import tempfile
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', action='store', dest='key_name', help='Key for value')
    parser.add_argument('-v', '--val', action='store', dest='val_name', help='Value to store')
    options = parser.parse_args()

if __name__ == '__main__':
    main()