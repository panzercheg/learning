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

    print('File size must be {sign} threshold {threshold} MB'.
          format(file=path_to_file, threshold=str(threshold), sign=sign))
    for root, dirs, files in os.walk(path_to_file):
        for file in files:
            if file.endswith(file_ext):
                path_to_file = os.path.join(root, file)
                size_byte = os.path.getsize(os.path.join(root, file))
                size_mb = size_byte / (1024 * 1024.0)
                size_mb = round(size_mb, 2)
                if not path_to_write:
                    without_write = comparison_size(int(threshold), size_mb, sign)
                    if without_write is True:
                        print('[Warning] Size file {file} is {size} MB and '
                              'file must be {sign} threshold {threshold} MB'.
                              format(file=path_to_file, size=size_mb, threshold=str(threshold), sign=sign))
                    elif path_to_write is False:
                        print('Size file {file} is ok {size} MB'.format(file=path_to_file, size=size_mb))
                    else:
                        print('Size file {file} is ok {size} MB'.format(file=path_to_file, size=size_mb))
                if path_to_write:
                    with open(path_to_write, 'a') as data:
                        with_write = comparison_size(int(threshold), size_mb, sign)
                        if with_write is False:
                            print('[Warning]'
                                  ' Size file {file} is {size} MB and file must be {sign} threshold {threshold} MB'.
                                  format(file=path_to_file, size=size_mb, threshold=str(threshold), sign=sign))
                            data.write('\n[Warning].'
                                       'Size file {file} is {size} MB and file must be {sign} threshold {threshold} MB'.
                                       format(file=path_to_file, size=size_mb, threshold=str(threshold), sign=sign))
                        else:
                            print('Size file {file} is ok {size} MB'.format(file=path_to_file, size=size_mb))
                            data.write('\nSize file {file} is ok {size} MB'.format(file=path_to_file, size=size_mb))


if __name__ == "__main__":
    parse_args()