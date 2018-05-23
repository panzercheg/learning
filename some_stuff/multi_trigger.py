import argparse
from scripts.jenkins.jenkins import Jenkins

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--starforce', action='store_true', dest='starforce', help='Build crypted by starforce')
parser.add_argument('-s', '--stream', action='store', dest='stream', help='stream')
parser.add_argument('-u', '--upstream', action='store', dest='upstream', help='upstream build number')
options = parser.parse_args()

stream = options.stream
upstream = options.upstream
starforce = options.starforce

build_templates = {
    'dev4': 't1_game_center_dev4_publish',
    'dev3': 't1_game_center_dev3_publish',
    'dev2': 't1_game_center_dev2_publish',
    'demo1': 't1_game_center_demo1_publish',
    'dev1': 't1_game_center_dev1_publish',
    'dev5': 't1_game_center_dev5_publish'
}

if stream == "master" and starforce:
    print(build_templates.get("dev5"))
    build_for_gamecenter = build_templates.get("dev5")

if stream == "master" and not starforce:
    print(build_templates.get("dev4"))
    build_for_gamecenter = build_templates.get("dev4")

if stream == "0.25" and starforce:
    print(build_templates.get("dev1"))
    build_for_gamecenter = build_templates.get("dev1")

if stream == "0.25" and not starforce:
    print(build_templates.get("dev3"))
    build_for_gamecenter = build_templates.get("dev3")

if stream == "0.24" and starforce:
    print(build_templates.get("demo1"))
    build_for_gamecenter = build_templates.get("demo1")

if stream == "0.24" and not starforce:
    print(build_templates.get("dev2"))
    build_for_gamecenter = build_templates.get("dev2")


def gamecenter_upload():
    params = {'json': {"parameter": [{"name": "BUILD_NUMBER", "value": upstream},
                                     {"name": "BUILD_BRANCH", "value": stream}]}}
    jenkins = Jenkins()
    jenkins.start_build_parametrized(build_for_gamecenter, params=params)

gamecenter_upload()