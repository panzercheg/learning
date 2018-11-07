#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pprint
import datetime
import sys
import json
import argparse
import re

sys.path.append(os.getcwd())

from some_stuff.mail_tools import MailTools
from some_stuff.file_actions import FileActions


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--qa', action='store', dest='qa_list', help='List QA for checkers')
    parser.add_argument('-r', '--repo', action='store', dest='repo', help='Path to repo')
    parser.add_argument('-s', '--since', action='store', dest='since', help='date since')
    parser.add_argument('-u', '--until', action='store', dest='until', help='date until')
    options = parser.parse_args()

    return options


def read_config(config):
    with open(config) as json_file:
        result = json.loads(json_file.read())
        return result


args = parse_args()
qa_list_templates = read_config(args.qa_list)


def mail_name(repo_name):
    now = datetime.datetime.now()
    curr_date = now.strftime("%d-%m-%Y")
    mail_subject = "Daily commit {} from repo {}".format(curr_date, repo_name)

    return mail_subject

new_list = set()
for value in qa_list_templates.values():
    new_list.update(value)


def mail_log(address, subject, message):
    mail = MailTools()
    mail.message(to=address, subject=subject,
                 message=message, fr='tech_email_account@youdomen.com')
    mail.send()


def get_git_log(repo, since, until, repo_name):
    res = []
    for key, value in qa_list_templates.items():
        res += value
    good_list = '|'.join(res)
    gitlog = FileActions().call('git log origin/master --pretty=format:"%an;;;%ai'
                                ' %s https://your_gitlab_url/{}/commit/%H"'
                                ' --author="{}"'
                                ' --since="{}"'
                                ' --until="{}"'.format(repo_name, good_list, since, until),
                                cd=repo,
                                return_output=True,
                                silent=True, output_encoding="utf-8")
    return gitlog[1]


def parse_git_data(parse_gitlog):
    globout = {}
    for name, value in qa_list_templates.items():
        name = name + '@mail.domen' # for send e-mail by list value
        globout[name] = []
        for _ in parse_gitlog.split('\n'):
            if len(_.split(';;;')) < 2:
                continue
            author, msg = _.split(';;;')
            if author in value:
                globout[name].append('{}, {}\n'.format(author, msg))

    return globout

sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)

if __name__ == '__main__':
    args = parse_args()
    print(args.qa_list)
    FileActions().call('git fetch origin', cd=args.repo, return_output=True, silent=True)
    FileActions().call('git config --global grep.extendedRegexp true', cd=args.repo, return_output=True, silent=True)
    (_, repo_name, _) = FileActions().call('git config --get remote.origin.url',
                                           cd=args.repo, return_output=True, silent=True)
    result = re.findall(r't1/(.*)\.', repo_name)
    result = ''.join(result)
    parse_gitlog = get_git_log(args.repo, args.since, args.until, result)
    out = parse_git_data(parse_gitlog)
    for key, value in out.items():
        pure_value = '\n'.join(value)
        mail_log(key, mail_name(result), pure_value)
    pprint.pprint(out)
