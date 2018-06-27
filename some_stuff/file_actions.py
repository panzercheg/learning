#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import stat
import time
import signal
import pickle
import shutil
import fnmatch
import hashlib
import argparse
import subprocess
import logging

from functools import partial
from multiprocessing.dummy import Process, Manager


class ProcessLoggerHandler:
    def __init__(self, process_logger, stdout_lvl=logging.INFO, stderr_lvl=logging.ERROR,
                 output_encoding=sys.stdout.encoding):
        self.process_logger = process_logger
        self.stdout_lvl = stdout_lvl
        self.stderr_lvl = stderr_lvl
        self.output_encoding = output_encoding

    def log_stdout(self, msg, *args, **kwargs):
        self.process_logger.log(self.stdout_lvl, msg, *args, **kwargs)

    def log_stderr(self, msg, *args, **kwargs):
        self.process_logger.log(self.stderr_lvl, msg, *args, **kwargs)

    def get_logger(self, stream_name):

        if stream_name == 'stderr':
            return self.log_stderr
        elif stream_name == 'stdout':
            return self.log_stdout
        else:
            return None

    def get_output_encoding(self):
        return self.output_encoding


class FileActions:
    @staticmethod
    def checksum(path, alg='md5', buff_size=4096):
        with open(path, mode='rb') as f:
            d = None
            if alg == 'sha1':
                d = hashlib.sha1()
            else:
                d = hashlib.md5()
            for buf in iter(partial(f.read, buff_size), b''):
                d.update(buf)
        return d.hexdigest()

    @staticmethod
    def remove(path):
        def remove_readonly(fn, path, excinfo):
            if fn is os.rmdir:
                os.chmod(path, stat.S_IWRITE)
                for root, dirs, files in os.walk(path):
                    for f in files:
                        full_path = os.path.join(root, f)
                        os.chmod(full_path, stat.S_IWRITE)
                shutil.rmtree(path)
            elif fn is os.remove:
                os.chmod(path, stat.S_IWRITE)
                os.remove(path)

        if os.path.isdir(path):
            shutil.rmtree(path, onerror=remove_readonly)
        elif os.path.isfile(path):
            os.remove(path)
        else:
            print('Neither fish nor fowl: ' + path)

    @staticmethod
    def copy(from_path, to_path, ignore=None):
        if os.path.isdir(from_path):
            return shutil.copytree(from_path, to_path, ignore=ignore)
        elif os.path.isfile(from_path):
            if not os.path.exists(os.path.dirname(to_path)):
                os.makedirs(os.path.dirname(to_path))
            return shutil.copyfile(from_path, to_path)

    @staticmethod
    def move(from_path, to_path, mask=[]):
        from_path = from_path.replace('\\', '/')
        to_path = to_path.replace('\\', '/')
        if os.path.isdir(from_path):
            for root, dirs, files in os.walk(from_path):

                filtered_files = []
                if mask:
                    for f in files:
                        for m in mask:
                            if fnmatch.fnmatch(f, m):
                                filtered_files.append(f)
                else:
                    filtered_files = files

                if filtered_files:
                    target_dir = to_path + root.replace(from_path, '')
                    if os.path.isfile(target_dir):
                        FileActions.remove(target_dir)
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    for f in filtered_files:
                        print(os.path.join(target_dir, f))
                        shutil.move(os.path.join(root, f), os.path.join(target_dir, f))
        elif os.path.isfile(from_path):
            return shutil.move(from_path, to_path)

    @staticmethod
    def chmod_plus_x(path):
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC)

    @staticmethod
    def check_call(code, ok_code=0):
        if code != ok_code:
            sys.exit(code)

    @staticmethod
    def call(command, cd=None, shell=False, return_output=False, write_pid_file=False, silent=False,
             output_encoding=sys.stdout.encoding, print_time=False, output_fh=None, timeout=None, env=(),
             socket_output=None, logger_handler=None):

        for i in env:
            os.environ[i[0]] = i[1]

        cwd = os.getcwd()
        start_time = time.clock()

        def pre_return(returncode):
            if cd:
                os.chdir(cwd)
            if not silent and print_time:
                call_time_s = int(time.clock() - start_time)
                call_time_m, call_time_s = divmod(call_time_s, 60)
                call_time_h, call_time_m = divmod(call_time_m, 60)
                call_time = '{:0>2}:{:0>2}:{:0>2}'.format(call_time_h, call_time_m, call_time_s)
                print('End of call {}> {} -- took {}, return code is {}\n'
                      ''.format(os.getcwd(), command, call_time, returncode))

        def process_streams(process_out, sys_out, process_manager_stream_dict, stream_name, h_logger=None):
            process_manager_stream_dict[stream_name] = b''
            process_logger_func = h_logger.get_logger(stream_name) if h_logger else None
            process_logger_output_encoding = h_logger.get_output_encoding() if h_logger else None

            for line in process_out:
                process_manager_stream_dict[stream_name] += line
                if not silent:
                    sys_out.buffer.write(line)
                if output_fh:
                    output_fh.write(line)
                if socket_output:
                    socket_output.sendall(pickle.dumps({'line': line}))
                if process_logger_func:
                    process_logger_func(str(line, process_logger_output_encoding).rstrip('\n\r'))

        def popen(proc_man_dict, popen_logger_handler=None):
            proc_man_dict['started'] = True
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
            if write_pid_file:
                FileActions.write_pid_file(proc.pid)

            err_thread = Process(target=process_streams,
                                 args=(proc.stderr, sys.stderr, process_manager_dict, 'stderr', popen_logger_handler))
            out_thread = Process(target=process_streams,
                                 args=(proc.stdout, sys.stdout, process_manager_dict, 'stdout', popen_logger_handler))
            err_thread.start()
            out_thread.start()
            err_thread.join()
            out_thread.join()

            proc.communicate()
            proc_man_dict['returncode'] = proc.returncode

        if cd:
            os.chdir(cd)
        if not silent:
            print('Call %s> %s' % (os.getcwd(), command))

        process_manager = Manager()
        process_manager_dict = process_manager.dict()
        process_manager_thread = Process(target=popen, args=(process_manager_dict, logger_handler))
        process_manager_thread.start()
        process_manager_thread.join(timeout)

        returncode = 0
        stderr = b''
        stdout = b''

        if not process_manager_thread.isAlive():
            returncode = process_manager_dict['returncode'] if 'returncode' in process_manager_dict else -100501
            stderr = process_manager_dict['stderr'] if 'stderr' in process_manager_dict else b'stderr capture error'
            stdout = process_manager_dict['stdout'] if 'stderr' in process_manager_dict else b'stdout capture error'
        else:
            class EmptyProcess:
                pass

            returncode = -100500
            if timeout:
                stderr = 'Process killed by timeout {timeout}'.format(timeout=timeout).encode()
            else:
                stderr = 'Execution error'.encode()

        pre_return(returncode)
        if return_output:
            return returncode, stdout.decode(output_encoding, 'replace'), stderr.decode(output_encoding, 'replace')
        else:
            return returncode

    @staticmethod
    def write_pid_file(pid):
        with open('{}.pid'.format(pid), 'w') as f:
            f.write(str(pid))
            f.close()

    @staticmethod
    def kill(path='.'):
        for f in os.listdir(path):
            name, ext = os.path.splitext(f)
            if ext == '.pid':
                try:
                    pid = int(name)
                except ValueError:
                    continue
                for child_pid in FileActions.get_child_processes(pid).keys():
                    print('kill child pid {}'.format(pid))
                    FileActions.kill_by_pid(child_pid)
                print('kill main pid {}'.format(pid))
                FileActions.kill_by_pid(pid)
                FileActions.remove(os.path.join(path, f))

    @staticmethod
    def kill_by_pid(pid):
        pid = int(pid)
        if sys.platform == 'win32':
            import ctypes
            PROCESS_TERMINATE = 1
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
            ctypes.windll.kernel32.TerminateProcess(handle, -1)
            ctypes.windll.kernel32.CloseHandle(handle)
        else:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    @staticmethod
    def get_child_processes(pid):
        pid = int(pid)
        result = {}
        if sys.platform == 'win32':
            wmic = FileActions.call('wmic process where (ParentProcessId={}) get Caption,ProcessId'.format(pid),
                                    shell=True, return_output=True, silent=True)
            if wmic and wmic[0] == 0:
                for p in wmic[1].replace('\r', '').split('\n'):
                    ps = p.split()
                    if ps and len(ps) == 2:
                        try:
                            result[int(ps[1])] = ps[0]
                        except ValueError:
                            continue
        else:
            import psutil
            try:
                for child in psutil.Process(pid).children(recursive=True):
                    result[child.pid] = child.pid
            except (FileNotFoundError, psutil.NoSuchProcess):
                pass
        return result

    @staticmethod
    def enum(enum_path, file_mask, all_dir=True):
        f = []
        for (root, dirs, files) in os.walk(enum_path):
            for file in files:
                if fnmatch.fnmatch(file, file_mask):
                    f.append(os.path.join(root, file))
        return f


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', action='store', dest='source', help='Source path', default=None)
    parser.add_argument('-t', '--target', action='store', dest='target', help='Target path', default=None)
    parser.add_argument('-c', '--copy', action='store_true', dest='copy', help='Copy action', default=False)
    parser.add_argument('-m', '--move', action='store_true', dest='move', help='Move action', default=False)
    parser.add_argument('--call', action='store', dest='call', help='Call command', default=None)
    parser.add_argument('--call_cd', action='store', dest='call_cd', help='Change dir before call', default=None)
    parser.add_argument('--mask', action='append', dest='mask', help='Mask', default=[])
    parser.add_argument('-g', '--get_child_processes', action='store', dest='get_child_processes',
                        help='Get child pids of process id', default=None)
    parser.add_argument('-k', '--kill', action='store_true', dest='kill', help='Kill processes by pid files',
                        default=False)
    parser.add_argument('--kill_path', action='store', dest='kill_path', help='Kill processes by pid files in path',
                        default='.')
    options = parser.parse_args()

    fa = FileActions()

    if options.kill:
        fa.kill(options.kill_path)

    if options.get_child_processes:
        print(fa.get_child_processes(options.get_child_processes))

    if options.source and options.target:
        if options.copy:
            fa.copy(options.source, options.target)
        elif options.move:
            fa.move(options.source, options.target, mask=options.mask)

    if options.call:
        fa.call(options.call, cd=options.call_cd, shell=True, print_time=True, write_pid_file=True)


if __name__ == '__main__':
    main()
