#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import ssl
from scripts.jenkins.jenkins import Jenkins

sys.path.append(os.getcwd())

# suppress certificate check
ssl._create_default_https_context = ssl._create_unverified_context

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--starforce', action='store_true', dest='starforce', help='Build crypted by starforce')
parser.add_argument('-s', '--stream', action='store', dest='stream', help='stream')
parser.add_argument('-u', '--upstream', action='store', dest='upstream', help='upstream build number')
parser.add_argument('-c', '--china', action='store_true', dest='china', help='Upload build to CN slot')
options = parser.parse_args()

stream = options.stream
upstream = options.upstream
starforce = options.starforce
china = options.china

if starforce and not china:
    build_type = stream + '_sf'
elif china:
    build_type = stream + '_cn'
else:
    build_type = stream

build_templates = {
    'master_sf': 'dev5',
    'master': 'dev4',
    '0.25': 'dev3',
    '0.25_sf': 'dev1',
    '0.24_sf': 'demo1',
    '0.24': 'dev2',
    '0.25_cn': 'cn_test',
    '0.24_cn': 'cn_test'
}

build_for_gamecenter = 't1_game_center_{}_publish'.format(build_templates.get(build_type))
print(build_for_gamecenter)


def gamecenter_upload():
    params = {'json': {"parameter": [{"name": "BUILD_NUMBER", "value": upstream},
                                     {"name": "BUILD_BRANCH", "value": stream}]}}
    jenkins = Jenkins()
    jenkins.start_build_parametrized(build_for_gamecenter, params=params)

gamecenter_upload()