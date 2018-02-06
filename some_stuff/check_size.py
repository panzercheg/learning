#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import argparse

__author__ = 'r.burenkov'


def comparison_size(i, j, action):
    cmp_size = {'>': -1,
                '<': 1}
    return cmp_size.get(action) * (i - j) > 0


def parse_args():
    def one_file(file_ext, path_to_file):
        size_byte = os.path.getsize(os.path.join(path_to_file))
        size_mb = size_byte / (1024 * 1024.0)
        size_mb = round(size_mb, 2)
        if path_to_file and not file_ext:
            check = os.path.isfile(path_to_file)
            if check is False:
                print('[Warning] file {} doesn`t exists!'.format(path_to_file))
            if check is True:
                file_size = comparison_size(int(threshold), size_mb, sign)
                if file_size is False:
                    print('[Warning] Size file {} is {} MB and '
                          'file must be {} threshold {} MB'.
                          format(path_to_file, size_mb, sign, str(threshold), ))
                else:
                    print('Size file {} is ok {} MB'.format(path_to_file, size_mb))

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', action='store', dest='file_path', help='Path for check size')
    parser.add_argument('-f', '--file', action='store', dest='file_write', help='Path for output file', default=False)
    parser.add_argument('-e', '--extensions', action='store', dest='file_ext', help='Extensions for checking',
                        default="")
    parser.add_argument('-t', '--threshold', action='store', dest='file_threshold',
                        help='Threshold for checking in Megabytes', default=100)
    parser.add_argument('-s', '--sign', action='store', dest='sign_check', help='Sign for comparison size, i.e. < >. '
                                                                                'File size _your_sign_ threshold',
                        default=">")
    options = parser.parse_args()
    path_to_file = options.file_path
    path_to_write = options.file_write
    file_ext = options.file_ext
    threshold = options.file_threshold
    sign = options.sign_check

    check = os.path.isfile(path_to_file)
    if check is True:
        one_file(file_ext, path_to_file)
    elif os.path.isdir(path_to_file):
        pass
    else:
        print('[Warning] file {} doesn`t exists!'.format(path_to_file))

    for root, dirs, files in os.walk(path_to_file):
        for file in files:
            if file.endswith(file_ext):
                path_to_file = os.path.join(root, file)
                size_byte = os.path.getsize(os.path.join(root, file))
                size_mb = size_byte / (1024 * 1024.0)
                size_mb = round(size_mb, 2)
                if not path_to_write:
                    without_write = comparison_size(int(threshold), size_mb, sign)
                    if without_write is False:
                        print('[Warning] Size file {} is {} MB and '
                              'file must be {} threshold {} MB'.
                              format(path_to_file, size_mb, sign, str(threshold), ))
                    else:
                        print('Size file {} is ok {} MB'.format(path_to_file, size_mb))
                if path_to_write:
                    with open(path_to_write, 'a') as data:
                        with_write = comparison_size(int(threshold), size_mb, sign)
                        if with_write is False:
                            print('[Warning]'
                                  ' Size file {} is {} MB and file must be {} threshold {} MB'.
                                  format(path_to_file, size_mb, sign, str(threshold)))
                            data.write('\n[Warning].'
                                       'Size file {} is {} MB and file must be {} threshold {} MB'.
                                       format(path_to_file, size_mb, sign, str(threshold)))
                        else:
                            print('Size file {} is ok {} MB'.format(path_to_file, size_mb))
                            data.write('\nSize file {} is ok {} MB'.format(path_to_file, size_mb))


if __name__ == "__main__":
    parse_args()