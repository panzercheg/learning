#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import fnmatch
import ftplib
import io
import os
import sys
import time
import xml.etree.ElementTree

sys.path.append(os.getcwd())

from some_stuff.agent_config import AgentConfig
from some_stuff.file_actions import FileActions


class FTPActions:

    def __init__(self, ftp_host_config_key='ftp_host', quiet=False):
        config = AgentConfig()
        self.user = config.get('ftp_login')
        self.passwd = config.get('ftp_password')
        self.host = config.get(ftp_host_config_key)
        self.ftp = ftplib.FTP(self.host, user=self.user, passwd=self.passwd)
        self.quiet = quiet
        self.meta_file_name = 'files_meta.xml'
        self.meta_file_data = {}
        self.tries = 8  # Default value for retry count
        self.delay = 10  # Default value for delay count in s

    '''
    Небольшая обёртка exception`ов:
    :self.tries - с каждой попыткой, уменьшаем количество попыток
    :self.delay - в начале, самый большой таймаут, далее пытаемся пробиться быстрее
    логика такая, что при обрыве соединения по любому поводу, мы устанавливаем реконект и продолжаем с конкретно
    упавшего события - если мы не смогли загрузить/скачать файл, то именно с него мы и продолжаем работу далее
    '''
    '''
    к конструкции "except OSError as err: if isinstance(err, OSError) and err.errno != 10048:"
     Т.к. в OSError есть сетевые ошибки, и локальные, и нет групппы под ошибку ниже,
      приходится делать вот такой вот блок
      OSError: [WinError 10048] Обычно разрешается только одно использование адреса сокета (протокол/сетевой адрес/порт)
       Из OSError обрабатываем только ошибку WinError 10048
    '''

    def except_ftp(self, exception, cur_dir=None):
        print("[ERROR] - {}".format(exception))
        self.tries -= 1
        if self.delay < 2560:  # multiplication delay by 2 every next try
            self.delay *= 2
        else:
            self.delay = 3600  # max delay is one hour
        if self.tries < 0:
            print("Try is over! ")
            sys.exit(1)
        print("Retrying with delay {} s... Try number {}".format(self.delay, self.tries))
        time.sleep(self.delay)
        self.ftp = ftplib.FTP(host=self.host, user=self.user, passwd=self.passwd)
        print("Connect established")
        if cur_dir:
            self.ftp.cwd(cur_dir)
        return

    def is_dir(self, name):
        try:
            pwd = self.ftp.pwd()
            self.ftp.cwd(name)
            self.ftp.cwd(pwd)
            return True
        except ftplib.all_errors:
            return False

    def get_meta_file(self, local_path):
        fd = io.StringIO()
        try:
            self.ftp.retrbinary('RETR ' + self.meta_file_name, lambda data: fd.write(data.decode()))
            fd.seek(0)
            meta_file_xml = xml.etree.ElementTree.fromstring(''.join(fd.readlines()))

            # clean up old meta data
            meta_root = None
            if 'root' in meta_file_xml.attrib:
                meta_root = meta_file_xml.attrib['root'].replace(self.ftp.pwd(), local_path).replace('\\', '/')
                for f in self.meta_file_data.copy():
                    if f.startswith(meta_root):
                        del (self.meta_file_data[f])

            for xml_current_file in meta_file_xml:
                stripped_path = xml_current_file.attrib['path'].replace(self.ftp.pwd(), local_path).replace('\\', '/')
                self.meta_file_data[stripped_path] = xml_current_file.attrib['md5']
            if not self.quiet:
                print('Using meta file ftp://{host}{path}'.
                      format(host=self.ftp.host,
                             path=os.path.join(self.ftp.pwd(),
                                               self.meta_file_name).replace('\\', '/')))
            return meta_root
        except ftplib.error_perm:
            if not self.quiet:
                print('No meta file')
            return None

    def down(self, remote_path, local_path=None, cleanup=True, ignore=[], ext=[]):
        try:
            if not local_path:
                local_path = os.path.split(remote_path)[1]

            if not self.is_dir(remote_path):
                self.get_one_file(local_path, remote_path, ignore=ignore, ext=ext)
                return

            self.ftp.cwd(remote_path)
            print(self.ftp.cwd(remote_path))
            self.get_meta_file(local_path)
            if cleanup:
                self.cleanup_local(local_path)
            self.get_recursive(local_path, cleanup=cleanup, ignore=ignore, ext=ext)

        except (ftplib.Error, TimeoutError, ConnectionResetError) as err:
            self.except_ftp(exception=err)
            self.down(remote_path, local_path, cleanup, ignore, ext)
            return
        except OSError as err:
            if isinstance(err, OSError) and err.errno != 10048:
                return
            self.except_ftp(exception=err)
            self.down(remote_path, local_path, cleanup, ignore, ext)
            return
        except PermissionError:
            print("[ERROR] - please check remote path! {}".format(remote_path))
            sys.exit(1)
        except WindowsError as winerr:
            print("[ERROR] - Check local path! {}".format(winerr))
            sys.exit(1)

    def cleanup_local(self, local_path):
        if not self.quiet:
            print('Clean up {path}'.format(path=local_path))
        if os.path.exists(local_path):
            if self.meta_file_data:
                for root, dirs, files in os.walk(local_path):
                    for item in files:
                        item_path = os.path.join(root, item)
                        if os.path.isfile(item_path) and item_path.replace('\\', '/') not in self.meta_file_data:
                            if not self.quiet:
                                print('rf ' + item_path)
                            FileActions.remove(item_path)
            else:
                FileActions.remove(local_path)

    def cleanup_remote(self, remote_path, file_list):
        try:
            for item in self.ftp.nlst(remote_path):
                if self.is_dir(item):
                    self.cleanup_remote(item, file_list)
                else:
                    if item not in file_list and os.path.split(item)[1] != self.meta_file_name:
                        if not self.quiet:
                            print('rf ftp://{host}{path}'.format(host=self.ftp.host, path=item))
                        self.ftp.delete(item)
        except (ftplib.Error, TimeoutError, ConnectionResetError) as err:
            self.except_ftp(exception=err)
            self.cleanup_remote(remote_path, file_list)
            return
        except OSError as err:
            if isinstance(err, OSError) and err.errno != 10048:
                return
            self.except_ftp(exception=err)
            self.cleanup_remote(remote_path, file_list)
            return
        except (FileNotFoundError,
                FileExistsError,
                BlockingIOError,
                IsADirectoryError,
                NotADirectoryError) as winerr:
            print("[ERROR] - Something get wrong! {}".format(winerr))
            sys.exit(1)

    def get_one_file(self, local_file_name, remote_file_name, ignore=[], ext=[]):
        # сохраняем каталог в дополнение к тому, какой у нас файл и
        # качаем определённый файл с определённого каталога
        if self.ftp.pwd():
            cur_dir = self.ftp.pwd()
        try:
            for current_ignore in ignore:
                if fnmatch.fnmatch(local_file_name, current_ignore):
                    if not self.quiet:
                        print('sf ' + local_file_name)
                    return
            if not ext:
                with open(local_file_name, 'wb') as local_file:
                    self.ftp.retrbinary('RETR ' + remote_file_name, local_file.write)
                    if not self.quiet:
                        print('df ' + local_file_name)
                    if self.tries < 8:  # reload tries and time after success ftp action
                        self.tries = 8
                        self.delay = 10
                    return
            else:
                for current_ext in ext:
                    if fnmatch.fnmatch(local_file_name, current_ext):
                        with open(local_file_name, 'wb') as local_file:
                            self.ftp.retrbinary('RETR ' + remote_file_name, local_file.write)
                            if not self.quiet:
                                print('df ' + local_file_name)
                            return

        except (ftplib.Error, TimeoutError, ConnectionResetError) as err:
            self.except_ftp(exception=err, cur_dir=cur_dir)
            self.get_one_file(local_file_name, remote_file_name, ignore, ext)
            return
        except OSError as err:
            if isinstance(err, OSError) and err.errno != 10048:
                return
            self.except_ftp(exception=err)
            self.get_one_file(local_file_name, remote_file_name, ignore, ext)
            return

    def get_recursive(self, local_path, cleanup=True, ignore=[], ext=[]):
        if self.ftp.pwd():
            cur_dir = self.ftp.pwd()
        try:
            if os.path.isfile(local_path):
                FileActions.remove(local_path)
            if not os.path.exists(local_path):
                os.makedirs(local_path)

            ls_items = self.ftp.nlst()
            if self.meta_file_name in ls_items and not self.is_dir(self.meta_file_name):
                del (ls_items[ls_items.index(self.meta_file_name)])
                meta_root = self.get_meta_file(local_path)
                if cleanup and meta_root:
                    self.cleanup_local(meta_root)

            next_dirs = []  # process dis after files for find meta file if exists
            for item in ls_items:
                if self.is_dir(item):
                    next_dirs.append(item)
                else:
                    local_file_name = os.path.join(local_path, item)
                    local_file_name_slash = local_file_name.replace('\\', '/')
                    if (local_file_name_slash in self.meta_file_data and
                            os.path.isfile(local_file_name) and
                            FileActions.checksum(local_file_name) == self.meta_file_data[local_file_name_slash]):
                        continue
                    else:
                        self.get_one_file(local_file_name, item, ignore=ignore, ext=ext)

            for item in next_dirs:
                next_local_path = os.path.join(local_path, item)
                self.ftp.cwd(item)
                self.get_recursive(next_local_path, ignore=ignore, ext=ext)
                self.ftp.cwd('..')
            return
        except (ftplib.Error, TimeoutError, ConnectionResetError) as err:
            self.except_ftp(exception=err, cur_dir=cur_dir)
            self.get_recursive(local_path=local_path, ignore=ignore, ext=ext, cleanup=True)
            return
        except OSError as err:
            if isinstance(err, OSError) and err.errno != 10048:
                return
            self.except_ftp(exception=err)
            self.get_recursive(local_path=local_path, ignore=ignore, ext=ext, cleanup=True)
            return
        except (FileNotFoundError,
                FileExistsError,
                BlockingIOError,
                IsADirectoryError,
                NotADirectoryError) as winerr:
            print("[ERROR] - Check local path! {}".format(winerr))
            sys.exit(1)

    def up_one_file(self, local_path, remote_path):
        self.upload_binary_file(local_path, remote_path)
        if not self.quiet:
            print('uf ' + remote_path)

    def up(self, local_path, remote_path, cleanup=True, erase_local=False, ignore=[], additional_meta=[]):
        remote_path = '/' + remote_path.strip('/')
        self.mkdirs(remote_path)

        strip_local_name = len(os.path.split(local_path)[0])
        full_remote_path = os.path.join(remote_path, os.path.split(local_path)[1]).replace('\\', '/')

        # one file
        if os.path.isfile(local_path):
            remote_file_name = local_path[strip_local_name:]
            remote_file_name = remote_file_name.strip('\\').strip('/')
            self.up_one_file(local_path, '{remote_dir}/{remote_file_name}'
                             .format(remote_dir=remote_path, remote_file_name=remote_file_name))
            return

        # get remote meta
        if self.is_dir(full_remote_path):
            self.ftp.cwd(full_remote_path)
            self.get_meta_file(local_path)

        files_meta_xml = xml.etree.ElementTree.Element('files', attrib={
            'datetime': str(time.time()),
            'root': os.path.join(remote_path, os.path.split(local_path)[1]).replace('\\', '/'),
        })
        files_meta_path = os.path.join(local_path, self.meta_file_name).replace('\\', '/')

        # upload recursive
        for root, dirs, files in os.walk(local_path):
            remote_dir = remote_path + '/' + root[strip_local_name:].replace('\\', '/').strip('/')
            self.mkdirs(remote_dir)
            for current_file in files:
                current_path = os.path.join(root, current_file).replace('\\', '/')
                skip = False
                for current_ignore in ignore:
                    if fnmatch.fnmatch(current_path, current_ignore):
                        skip = True
                if current_file.startswith('.'):  # always skip files like .gitignore
                    print('skipping {} . Please, never upload dot files to ftp'.format(current_path))
                    skip = True
                if skip or current_path == files_meta_path:
                    continue
                current_remote_path = remote_dir + '/' + current_file
                md5 = str(FileActions.checksum(current_path))
                size = os.path.getsize(current_path)
                if current_path in self.meta_file_data and self.meta_file_data[current_path] == md5:
                    pass  # leave remote
                else:
                    self.up_one_file(current_path, current_remote_path)

                files_meta_xml.append(xml.etree.ElementTree.Element('file', attrib={
                    'md5': md5, 'path': current_remote_path, 'size': str(size)}))

        for current_additional_meta in additional_meta:
            additional_files_meta_path = os.path.join(current_additional_meta, self.meta_file_name).replace('\\', '/')
            additional_meta_remote_path = (remote_path + '/' +
                                           current_additional_meta[strip_local_name:].replace('\\', '/').strip('/'))
            additional_files_meta_xml = xml.etree.ElementTree.Element('files', attrib={
                'datetime': str(time.time()),
                'root': additional_meta_remote_path})
            for file_xml in files_meta_xml:
                if file_xml.attrib['path'].startswith(additional_meta_remote_path):
                    additional_files_meta_xml.append(file_xml)
            self.write_and_upload_meta(additional_files_meta_path, os.path.join(
                additional_meta_remote_path, self.meta_file_name).replace('\\', '/'), additional_files_meta_xml)

        # write and upload new main meta
        self.write_and_upload_meta(files_meta_path, os.path.join(
            remote_path, os.path.split(local_path)[1],
            os.path.split(files_meta_path)[1]).replace('\\', '/'), files_meta_xml)
        # cleanup_remote
        if cleanup:
            self.cleanup_remote(full_remote_path, [path.attrib['path'] for path in files_meta_xml.iter('file')])

        if erase_local:
            self.erase_local(local_path)

    @staticmethod
    def erase_local(local_path):
        print('rf ' + local_path)
        FileActions.remove(local_path)

    def upload_binary_file(self, local_path, remote_path):
        if self.ftp.pwd():
            cur_dir = self.ftp.pwd()
        try:
            self.ftp.storbinary('STOR ' + remote_path, open(local_path, 'rb'))
            if self.tries < 8:  # reload tries after success ftp action
                self.tries = 8
                self.delay = 10
            return
        except (ftplib.Error, TimeoutError, ConnectionError) as err:
            self.except_ftp(exception=err, cur_dir=cur_dir)
            self.upload_binary_file(local_path=local_path, remote_path=remote_path)
            return
        except OSError as err:
            if isinstance(err, OSError) and err.errno != 10048:
                return
            self.except_ftp(exception=err)
            self.upload_binary_file(local_path=local_path, remote_path=remote_path)
            return
        except FileNotFoundError:
            print("[ERROR] - check local path! {}".format(local_path))
            sys.exit(1)

    def write_and_upload_meta(self, local_path, remote_path, xml_data):
        try:
            print(remote_path)
            with open(local_path, 'wb') as local_file:
                xml.etree.ElementTree.ElementTree(xml_data).write(local_file, encoding="utf-8", xml_declaration=True)

            self.upload_binary_file(local_path, remote_path)
        except FileNotFoundError:
            print("[ERROR] - check local path! {}".format(local_path))
            sys.exit(1)

    def mkdirs(self, path):
        path_splitted = path.replace('\\', '/').split('/')
        path_temp = ''
        for current_dir in path_splitted:
            path_temp += current_dir + '/'
            if not self.is_dir(path_temp):
                self.ftp.mkd(path_temp)

    def clear(self, remote_path, leave_last=0):
        pwd = self.ftp.pwd()
        self.ftp.cwd(remote_path)

        list_dir = []
        if leave_last != 0:
            list_dir = [int(i) for i in self.ftp.nlst() if i.isdigit()]
        else:
            list_dir = self.ftp.nlst('-a')
            list_dir.remove('.')
            list_dir.remove('..')

        for item in sorted(list_dir, reverse=True)[leave_last:]:
            item = str(item)
            if self.is_dir(item):
                self.clear(item)
            else:
                try:
                    self.ftp.delete(item)
                except ftplib.error_perm as e:
                    print('[ERROR] Cannot remove {path} because {err}'.format(path=item, err=e))

        self.ftp.cwd(pwd)
        if not leave_last:
            try:
                self.ftp.rmd(remote_path)
            except ftplib.error_perm as e:
                print('[ERROR] Cannot remove {path} because {err}'.format(path=remote_path, err=e))

    @staticmethod
    def __normpath(path):
        result = path
        result = result.replace('//', '/')
        if len(result) > 0 and result[-1:] == '/':
            result = result[:-1]
        if len(result) > 0 and result[0] == '/':
            result = result[1:]
        return result

    def exists(self, path):
        result = False
        path = self.__normpath(path)
        head, tail = os.path.split(path)
        head = self.__normpath(head)
        for name in self.ftp.nlst(head):
            if name == (head + '/' + tail if len(head) > 0 else tail):
                result = True
                break
        return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--upload', action='store_true', dest='upload', help='Action "upload"', default=False)
    parser.add_argument('-d', '--download', action='store_true', dest='download', help='Action "download"',
                        default=False)
    parser.add_argument('-c', '--clear', action='store', dest='clear', help='Clear specified path on the server',
                        default=None)
    parser.add_argument('-l', '--local_path', action='store', dest='local_path', help='Local path', default=None)
    parser.add_argument('-r', '--remote_path', action='store', dest='remote_path', help='Remote path', default=None)
    parser.add_argument('-a', '--additional_meta', action='append', dest='additional_meta',
                        help='Generate additional meta file for directory on upload', default=[])
    parser.add_argument('-o', '--leave_last', action='store', dest='leave_last', help='Leave only last N items',
                        default=0)
    parser.add_argument('-n', '--no_cleanup', action='store_false', dest='cleanup',
                        help='Do not clean up local directory on download action', default=True)
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet', help='Quiet mode', default=False)
    parser.add_argument('-i', '--ignore', action='append', dest='ignore',
                        help='Ignore files for uploading or downloadaing by mask', default=[])
    parser.add_argument('-m', '--extension', action='append', dest='extension',
                        help='Ignore all files, except extension for uploading or downloadaing by mask', default=[])
    parser.add_argument('-e', '--erase', action='store_true', dest='erase',
                        help='Remove directory from local path', default=False)
    parser.add_argument('--exists', action='store_true', dest='exists',
                        help='Check if file or directory exists on ftp-server', default=False)
    parser.add_argument('--hostname', action='store', dest='override_hostname', help='Property name from agent config',
                        default=None)
    parser.add_argument('--username', action='store', dest='override_username', help='Property name from agent config',
                        default=None)
    parser.add_argument('--userpass', action='store', dest='override_userpass', help='Property name from agent config',
                        default=None)
    options = parser.parse_args()

    ftp = FTPActions(quiet=options.quiet)

    if options.override_hostname and options.override_username and options.override_userpass:
        config = AgentConfig()
        ftp.ftp = ftplib.FTP(config.get(options.override_hostname), user=config.get(options.override_username),
                             passwd=config.get(options.override_userpass))

    else:
        print('Using default hostname, username and password. Please specify every of them to override')

    if options.clear:
        ftp.clear(options.clear, int(options.leave_last))

    if options.exists:
        if options.remote_path:
            sys.exit(0) if ftp.exists(options.remote_path) else sys.exit(1)
        else:
            print('Need remote paths. See help for options.')

    if options.download:
        if options.remote_path:
            ftp.down(options.remote_path, options.local_path, cleanup=options.cleanup, ignore=options.ignore,
                     ext=options.extension)
        else:
            print('Need remote paths. See help for options.')
    elif options.upload:
        if options.remote_path and options.local_path:
            ftp.up(options.local_path, options.remote_path, cleanup=options.cleanup, erase_local=options.erase,
                   ignore=options.ignore, additional_meta=options.additional_meta)
        else:
            print('Need local and remote paths. See help for options.')


if __name__ == '__main__':
    main()
