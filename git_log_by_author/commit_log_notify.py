#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pprint
import datetime
import sys

sys.path.append(os.getcwd())

from some_stuff.mail_tools import MailTools
from some_stuff.file_actions import FileActions


qa_list_templates = {
    'prefix_qa_for_send_mail': ['git author'] # 'j.smith': ['j.jonson', 'b.pitt', 't.hardy']
}

now = datetime.datetime.now()
curr_date = now.strftime("%d-%m-%Y")
mail_subject = "Daily commit {}".format(curr_date)

new_list = set()
for value in qa_list_templates.values():
    new_list.update(value)


def mail_log(address, subject, message):
    mail = MailTools()
    mail.message(to=address, subject=subject,
                 message=message, fr='tech_email_account@youdomen.com')
    mail.send()


def get_git_log(repo):
    res = []
    for key, value in qa_list_templates.items():
        res += value
    good_list = '|'.join(res)
    gitlog = FileActions().call('git log origin/master --pretty=format:"%an;;;%ai'
                                ' %s https://your_gitlab_url/commit/%H"'
                                ' --author="{}"'
                                ' --since="yesterday 07:00"'
                                ' --until="today 07:00"'.format(good_list),
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


sys.stdout = open(1, 'w', encoding='utf-8', closefd=False) # for right output from pprint(out)

if __name__ == '__main__':
    repo = sys.argv[1]
    FileActions().call('git fetch origin', cd=repo, return_output=True, silent=True)
    parse_gitlog = get_git_log(repo)
    out = parse_git_data(parse_gitlog)
    for key, value in out.items():
        pure_value = '\n'.join(value)
        mail_log(key, mail_subject, pure_value)
    pprint.pprint(out)
