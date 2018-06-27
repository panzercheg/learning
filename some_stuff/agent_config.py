#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
sys.path.append(os.getcwd())

import json
import platform
from some_stuff.file_actions import FileActions


class AgentConfigException(Exception):
    pass


class AgentConfig:
    def __init__(self):
        self.config = self.read_config()

    def read_config(self):
        config_name = 'agent_config.json'
        config_path = ''
        if platform.system() == 'Linux':
            if 'HOME' in os.environ:
                config_path = os.path.join(os.getenv('HOME'), config_name)
            else:
                home = FileActions.call('getent passwd `whoami` | cut -d: -f6', return_output=True,
                                        shell=True, silent=True)[1].strip()
                config_path = os.path.join(home, config_name)
        elif platform.system() == 'Windows':
            config_path = os.path.join(os.getenv('USERPROFILE'), config_name)
        else:
            print('Unknown OS')

        return self.parse_json(config_path)

    @staticmethod
    def parse_json(config_file):
        try:
            with open(config_file) as config_file:
                return json.load(config_file)
        except Exception as e:
            raise AgentConfigException(e)

    def get(self, key):
        if self.config and key in self.config:
            return self.config[key]


def main():
    config = AgentConfig()
    print(config.get('gitlab_api_url'))


if __name__ == '__main__':
    main()
