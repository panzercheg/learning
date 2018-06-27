import argparse
import sys
import os
import smtplib

sys.path.append(os.getcwd())

from some_stuff.agent_config import AgentConfig
from email.mime.text import MIMEText


class MailTools():
    def __init__(self, message='', fr='', to='', subject='', server='smtp.server:Port', tls=True):
        self.msg = message
        self.fr = fr
        self.to = to
        self.subject = subject
        self.server = server
        self.tls = tls
        self.__srv = self.__server_init()
        self.__message = None
        self.__construct_message()

    def __server_init(self):
        srv = smtplib.SMTP(self.server)
        srv.ehlo()

        if self.tls:
            srv.starttls()

        config = AgentConfig()
        if not self.fr:
            self.fr = config.get('email_login')
        try:
            srv.login(user=config.get('email_login'), password=config.get('email_password'))
        except smtplib.SMTPException as e:
            print('Cannot login to SMTP server, {}'.format(e))
        return srv

    def send(self):
        self.__construct_message()
        self.__srv.send_message(self.__message)
        self.__srv.close()

    def __construct_message(self):
        self.__message = MIMEText(self.msg)
        self.__message['Subject'] = self.subject
        self.__message['From'] = self.fr
        self.__message['To'] = self.to

    def message(self, to='', fr='', subject='', message=''):
        if to:
            self.to = to
        if fr:
            self.fr = fr
        if subject:
            self.subject = subject
        if message:
            self.msg = message


def get_args():
    this = argparse.ArgumentParser()
    this.add_argument('--subject', '-s', type=str, default=None, required=True)
    this.add_argument('--message', '-m', type=str, default=None, required=True)
    this.add_argument('--to', '-t', type=str, default=None, required=True)
    this.add_argument('--fr', '-f', type=str, default=None, required=True)

    return this.parse_args()


if __name__ == '__main__':
    args = get_args()
    #  for testing only!
    mail = MailTools()
    mail.message(to=args.to)
    mail.message(subject=args.subject, message=args.message, fr=args.fr)
    mail.send()
