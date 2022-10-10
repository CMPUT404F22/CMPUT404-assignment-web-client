#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

from http import server
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class URLParser(object):
    def __init__(self, url):
        self.parsed_url = urllib.parse.urlparse(url)
    
    def get_host(self):
        return self.parsed_url.hostname

    def get_port(self):
        if self.parsed_url.port is None:
            return 80
        return self.parsed_url.port
    
    def get_request_path(self):
        if len(self.parsed_url.path) > 0:
            return self.parsed_url.path
        return "/"
    
class ServerResponseParser(object):
    def __init__(self, server_response: str):
        self.server_response = server_response
        self.parse_data(server_response)
    
    def parse_data(self, server_response: str):
        data = server_response.splitlines()
        self.status_code = int(data[0].split(" ")[1])
        self.body = data[-1]


class HTTPClient(object):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    # Reference: 
    # Source: https://stackoverflow.com/a/30686735
    # Date Accessed: 2022/10/10
    def utf8len(self, s: str):
        return len(s.encode("utf-8"))
    
    def http_get_request(self, path, host):
        request = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n'
        return request
    
    def http_post_request(self, path, host, args=None):
        request = f'POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\n'
        body = ""
        if args:
            for key, value in args.items():
                body += f'{key}={value}&'
        body = body.strip("&")
        
        request += f'Content-Length: {self.utf8len(body)}\r\n\r\n{body}\r\n'
        return request

    def GET(self, url, args=None):
        url_parser = URLParser(url)
        self.connect(url_parser.get_host(), url_parser.get_port())
        self.sendall(
            self.http_get_request(
                url_parser.get_request_path(),
                url_parser.get_host()
            )
        )
        data = self.recvall(self.socket)
        server_response = ServerResponseParser(data)
        
        self.close()
        return HTTPResponse(server_response.status_code, server_response.body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        url_parser = URLParser(url)
        self.connect(url_parser.get_host(), url_parser.get_port())
        self.sendall(
            self.http_post_request(
                url_parser.get_request_path(),
                url_parser.get_host(),
                args=args
            )
        )
        data = self.recvall(self.socket)
        server_response = ServerResponseParser(data)
        
        self.close()
        return HTTPResponse(server_response.status_code, server_response.body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
