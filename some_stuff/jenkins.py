#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import urllib.request
from base64 import b64encode


sys.path.append(os.getcwd())
from some_stuff.agent_config import AgentConfig


class Jenkins:

    def __init__(self):
        # Proxy disabler
        proxy = urllib.request.ProxyHandler(proxies={})
        opener = urllib.request.build_opener(proxy)
        urllib.request.install_opener(opener)

        config = AgentConfig()
        self.host = config.get('jenkins_url')
        login = config.get('jenkins_login')
        token = config.get('jenkins_token')
        if not login or not token or not self.host:
            raise PermissionError
        self.auth_header = b64encode('{login}:{token}'.format(login=login, token=token).encode()).decode("ascii")

    def get_build_info(self, job, number, encoding='utf-8'):
        request = urllib.request.Request('{host}/job/{job}/{number}/api/json'.format(
            host=self.host, job=job, number=number))
        request.add_header('Authorization', 'Basic %s' % self.auth_header)
        answer = urllib.request.urlopen(request)
        answer = answer.read().decode(encoding)
        return json.loads(answer)

    def get_build_changed_files(self, job, number, action=['edit', 'add']):
        '''
        :param action: ['edit', 'add', 'delete']
        '''
        result = []
        build_info = self.get_build_info(job, number)
        if 'changeSet' in build_info and 'items' in build_info['changeSet']:
            for x in build_info['changeSet']['items']:
                if 'paths' in x:
                    for y in x['paths']:
                        if 'editType' in y and y['editType'] in action:
                            result.append(y['file'])
        return result

    def get_build_commit_messages(self, job, number):
        result = []
        build_info = self.get_build_info(job, number)
        if 'changeSet' in build_info and 'items' in build_info['changeSet']:
            for x in build_info['changeSet']['items']:
                if 'comment' in x and 'author' in x and 'fullName' in x['author']:
                    result.append([x['author']['fullName'], x['comment']])
        return result

    def start_build_parametrized(self, job, params={}, encoding='utf-8'):
        request_params = urllib.parse.urlencode(params).encode(encoding)
        request = urllib.request.Request('{host}/job/{job}/build'.format(host=self.host, job=job))
        request.method = 'POST'
        request.add_header('Authorization', 'Basic %s' % self.auth_header)
        return urllib.request.urlopen(request, bytes(request_params))

    def download_build_artifacts(self, job, artifacts, target_dir='.'):
        for name in artifacts:
            request = urllib.request.Request(
                '{host}/job/{job}/lastSuccessfulBuild/artifact/{name}'.format(host=self.host, job=job, name=name))
            request.add_header('Authorization', 'Basic %s' % self.auth_header)
            answer = urllib.request.urlopen(request)
            with open(os.path.abspath(os.path.join(target_dir, name)), 'wb') as f:
                shutil.copyfileobj(answer, f)

    def get_build_parameter(self, job, number, parameter_name):
        for action in list(filter(
                lambda action: action.get('_class') == 'com.tikal.jenkins.plugins.multijob.MultiJobParametersAction',
                self.get_build_info(job, number).get('actions', []))):
            for parameter in list(
                    filter(lambda parameter: parameter.get('name') == parameter_name, action.get('parameters', []))):
                return parameter.get('value')

    def get_build_with_parameteres(self, job, parameters):
        for action in list(filter(
                lambda action: action.get('_class') == 'com.tikal.jenkins.plugins.multijob.MultiJobParametersAction',
                self.get_build_info(job, number).get('actions', []))):
            for parameter in list(
                    filter(lambda parameter: parameter.get('name') == parameter_name, action.get('parameters', []))):
                return parameter.get('value')


def main():
    jenkins = Jenkins()


if __name__ == '__main__':
    main()