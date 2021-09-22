#  coding: utf-8
import socket
import socketserver
from typing import List, Tuple

import requests

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2021 Ray Gong

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/
import os
from os import path, replace

wwwDir = path.join(
    os.path.dirname(os.path.realpath(__file__)), "www"
)  # https://stackoverflow.com/a/5137509/12471420


badMethods = {"CONNECT", "DELETE", "HEAD",
              "OPTIONS", "OPTIONS", "POST", "PUT", "TRACE"}


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()

        print("Got a request of:")
        print(self.data.decode(), "\n")
        self.request: socket.socket = self.request

        lines = self.data.decode().split("\n")
        header = lines[0].split()  # something like Get, /, HTTP/1,1

        print(header, "\n")
        # self.request.sendall(bytearray(f"HTTP/1.1 200 OK", "utf-8"))
        # return
        if not header:
            self.request.sendall(
                bytearray(f"HTTP/1.1 400 Bad Request", "utf-8"))

        elif header[0] == "GET":

            dir = path.join(
                wwwDir, header[1][1:].replace(
                    "\\", os.sep).replace("/", os.sep)
            )  # replacing slashes to work on both windows and unix systems, removing initial slash so python doesnt treat it as abs path
            print(dir, wwwDir,  path.isfile(
                dir), dir[-1] == os.sep and path.isfile(dir[:-1]), self.is_in_directory(dir, wwwDir))
            if not self.is_in_directory(dir, wwwDir):
                self.request.sendall(
                    bytearray(
                        f"HTTP/1.1 404 NOT FOUND\n\n ",
                        "utf-8",
                    ))

            elif path.isdir(dir):
                if dir[-1] == os.sep:
                    self.handleFolder(dir)
                else:

                    for line in lines:
                        if line.split(' ')[0] == 'Host:':
                            host = line.split(" ")[1].strip()
                            break
                    else:
                        host = 'localhost:8080'

                    print(
                        f"HTTP/1.1 301 Moved Permanently \nLocation:http://{host}{header[1]}/\n\n ")
                    self.request.sendall(
                        bytearray(
                            f"HTTP/1.1 301 Moved Permanently \nLocation:http://{host}{header[1]}/\n\n ",
                            "utf-8",
                        )
                    )
            elif path.isfile(dir):
                self.handleFile(dir)
            elif dir[-1] == os.sep and path.isfile(dir[:-1]):
                self.handleFile(dir[:-1])
            else:
                self.request.sendall(
                    bytearray(
                        f"HTTP/1.1 404 NOT FOUND\n\n ",
                        "utf-8",
                    ))

        elif header[0] in badMethods:
            self.request.sendall(
                bytearray(f"HTTP/1.1 405 Method Not Allowed", "utf-8"))
        else:
            self.request.sendall(
                bytearray(f"HTTP/1.1 400 Bad Request", "utf-8"))

    def is_in_directory(self, filepath, directory):
        # https://stackoverflow.com/a/47347518/12471420
        print('is in dir', os.path.realpath(
            filepath), os.path.realpath(directory))
        return os.path.realpath(filepath).startswith(
            os.path.realpath(directory) + os.sep) or os.path.realpath(filepath) == os.path.realpath(directory)

    def handleFolder(self, dir: str):
        # if dir is a valid folder path
        for item in os.listdir(dir):
            if item[-5:] == ".html" or item[-4:] == ".htm":
                with open(path.join(dir, item), "r", encoding="utf-8") as f:
                    self.request.sendall(
                        bytearray(
                            f"HTTP/1.1 200 OK \nContent-Type: text/html \n\n {f.read()}", "utf-8")
                    )
                break

    def handleFile(self, dir: str):
        with open(dir, "r", encoding="utf=8") as f:
            contentType = None
            if dir[-5:] == ".html" or dir[-4:] == ".htm":
                contentType = "Content-Type: text/html"
            elif dir[-4:] == ".css":
                contentType = "Content-Type: text/css"
            self.request.sendall(
                bytearray(
                    f"HTTP/1.1 200 OK \n{contentType if contentType is not None else ''} \n\n {f.read()}",
                    "utf-8",
                )
            )


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    with open('bruh', 'w') as p:
        p.write('started')

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
