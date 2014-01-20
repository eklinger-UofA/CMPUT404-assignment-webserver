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


HTTP_VERSION = "HTTP/1.1"
END_LINE = "\r\n"

class MyWebServer(SocketServer.BaseRequestHandler):

    def handle(self):
        self.responseDict = {}
        self.data = self.request.recv(1024).strip()
        lines = self.data.splitlines()
        requestHeader = lines[0]
        tokens = requestHeader.split(" ")
        path = tokens[1]

        if self.generateResponseFromPath(path):
            httpResponse = self.buildResponse()
        else:
            httpResponse = self.build404()
        self.request.sendall(httpResponse)

    def generateResponseFromPath(self, path):

        wwwDirPath = os.path.join(os.getcwd(), "www")

        if path.endswith(".html"):
            htmlPath = os.path.join(wwwDirPath, path.lstrip('/'))
            if os.path.exists(htmlPath) and os.path.isfile(htmlPath):
                fileContents = self.readFileContents(htmlPath)
                if fileContents:
                    self.responseDict["body"] = fileContents
                    self.responseDict["return-code"] = "200 OK"
                    self.responseDict["content-type"] = "Content-Type: text/html"
                    return True
            return False
        elif path.endswith(".css"):
            cssPath = os.path.join(wwwDirPath, path.lstrip('/'))
            if os.path.exists(cssPath) and os.path.isfile(cssPath):
                fileContents = self.readFileContents(cssPath)
                if fileContents:
                    self.responseDict["body"] = fileContents
                    self.responseDict["return-code"] = "200 OK"
                    self.responseDict["content-type"] = "Content-Type: text/css"
                    return True
            return False
        else:
            indexPath = os.path.join(wwwDirPath, path.lstrip('/'), "index.html")
            if os.path.exists(indexPath) and os.path.isfile(indexPath):
                fileContents = self.readFileContents(indexPath)
                if fileContents:
                    self.responseDict["body"] = fileContents
                    self.responseDict["return-code"] = "200 OK"
                    self.responseDict["content-type"] = "Content-Type: text/html"
                    return True
            return False

    def readFileContents(self, filePath):
        """ Reads """
        try:
            openFile = open(filePath)
            fileContents = openFile.read()
            openFile.close()
            return fileContents
        except:
            return False

    def buildResponse(self):
        """
        using the response dict filled earlier build and return the http response
        """
        httpResponse = ""
        httpResponse += HTTP_VERSION
        httpResponse += " "
        httpResponse += self.responseDict["return-code"]
        httpResponse += END_LINE
        httpResponse += self.responseDict["content-type"]
        httpResponse += END_LINE
        httpResponse += END_LINE
        httpResponse += self.responseDict["body"]
        return httpResponse

    def build404(self):
        """
        """
        httpResponse = ""
        httpResponse += HTTP_VERSION
        httpResponse += " "
        httpResponse += "404 Not Found"
        httpResponse += END_LINE
        httpResponse += END_LINE
        httpResponse += "404 Not Found"
        return httpResponse


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
