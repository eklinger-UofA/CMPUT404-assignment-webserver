# coding: utf-8

import os
import SocketServer

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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

class MyWebServer(SocketServer.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)
        print ("Got a request")
        lines = self.data.splitlines()
        for line in lines:
            print (line)
        requestHeader = lines[0]
        tokens = requestHeader.split(" ")
        print ("tokens of the request header are as follows")
        for token in tokens:
            print (token)
        method = tokens[0]
        path = tokens[1]
        http = tokens[2]
        # I want to get all the directories listed where the web server is hosted
        wwwDir = self.getWWWDirectoryIfItExists()
        if wwwDir:
            # Gotta look for the index.html OR serve the 303 file
            #self.request.sendall("www dir found, need to see if index.html exists")
            if self.doesIndexExist(wwwDir):
                # server the index page as the reponse
                #self.request.sendall("Found index.html, time to serve it")
                try:
                    f = open(os.path.join(wwwDir, "index.html"))
                    fileContents = f.read()
                    self.request.sendall(fileContents)
                except:
                    self.request.sendall("Failed to open index.html")
                    raise Exception("Stuff is broken!")
                finally:
                    if f:
                        f.close()
            else:
                # serve a missing file warning, 303, etc
                self.request.sendall("No index.html found")
        else:
            # Report as error since there is no www dir being served
            self.request.sendall("No www dir located in current working directory")
        self.request.sendall("OK")

    def getWWWDirectoryIfItExists(self):
        cwd = os.getcwd()
        wwwDir = os.path.join(cwd, "www")
        if os.path.exists(wwwDir) and os.path.isdir(wwwDir):
            return wwwDir
        return None

    def doesIndexExist(self, wwwDir):
        indexPath = os.path.join(wwwDir, "index.html")
        if os.path.exists(indexPath) and os.path.isfile(indexPath):
            return True
        return False


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
