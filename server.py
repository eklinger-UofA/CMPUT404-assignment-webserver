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


# Example of a HTTP request
'''
GET /path/file.html HTTP/1.0
From: someuser@jmarshall.com
User-Agent: HTTPTool/1.0
[blank line here]
'''
# and an exmaple of a HTTP response
'''
HTTP/1.0 200 OK
Date: Fri, 31 Dec 1999 23:59:59 GMT
Content-Type: text/html
Content-Length: 1354

<html>
<body>
<h1>Happy New Millennium!</h1>
(more file contents)
  .
    .
      .
</body>
</html>
'''

HTTP_VERSION = "HTTP/1.1"
END_LINE = "\r\n"

class MyWebServer(SocketServer.BaseRequestHandler):

    def handle(self):
        # I want this dict to have the following values, to be used to contruct the response later
        # 1 return code: depending on what is the result of the path
        # 2 return text: To follow the return code
        # 3 Date: time that the response is returned
        # 4 content-type: either text/html if a html file, or test/css if its a css file
        # optional content length?
        # the result from reading the file, if one was found (the contents of index.html)
        self.responseDict = {}
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)
        print ("Got a request")
        lines = self.data.splitlines()
        for line in lines:
            print (line)
        requestHeader = lines[0]
        tokens = requestHeader.split(" ")
        #print ("tokens of the request header are as follows")
        #for token in tokens:
        #    print (token)
        #method = tokens[0]
        path = tokens[1]
        #http = tokens[2]

        if self.generateResponseFromPath(path):
            httpResponse = self.buildResponse()
        else:
            httpResponse = self.build404()
        self.request.sendall(httpResponse)

    def generateResponseFromPath(self, path):

        wwwDirPath = os.path.join(os.getcwd(), "www")
        # first need to check the path
        # MOVE this to the bottom as an else
        if path.endswith('/'): # this could probably be changed to "endswith" and cover more cases
            # This is a directory, so we need to serve index.html from this directory if it exists
            if path == '/':
                # Not needed, the one in the else works for all
                indexPath = os.path.join(wwwDirPath, "index.html")
            else:
                indexPath = os.path.join(wwwDirPath, path.lstrip('/'), "index.html")
            if not self.checkPath(indexPath, wwwDirPath):
                print "Found out the path doesnt exist, or its trying to access something it should be"
                return False
            if os.path.exists(indexPath) and os.path.isfile(indexPath):
                # read the file, get the contexts and save it in the response dict
                try:
                    indexFile = open(indexPath)
                    fileContents = indexFile.read()
                    self.responseDict["body"] = fileContents
                    indexFile.close()
                    self.responseDict["return-code"] = "200 OK"
                    self.responseDict["content-type"] = "Content-Type: text/html"
                    return True
                except:
                    return False
            else: # the file doesnt exsist, need to return the proper error code and return
                return False
        # now we know we arent dealing with a directory, so it much be a file (if it is in fact a valid url)
        elif path.endswith(".html"):
            print "detected a .html file"
            print "wwwDirPath: %s" % wwwDirPath
            print "path: %s" % path
            htmlPath = os.path.join(wwwDirPath, path.lstrip('/'))
            print "html path file path is: %s" % htmlPath
            if not self.checkPath(htmlPath, wwwDirPath):
                return False
            if os.path.exists(htmlPath) and os.path.isfile(htmlPath):
                # read the file, get the contexts and save it in the response dict
                try:
                    htmlFile = open(htmlPath)
                    fileContents = htmlFile.read()
                    self.responseDict["body"] = fileContents
                    htmlFile.close()
                    self.responseDict["return-code"] = "200 OK"
                    self.responseDict["content-type"] = "Content-Type: text/html"
                    return True
                except:
                    return False
            else: # html file doesnt exsist, need to return proper error code
                return False
        elif path.endswith(".css"):
            print "detected a .css file"
            print "wwwDirPath: %s" % wwwDirPath
            print "path: %s" % path
            cssPath = os.path.join(wwwDirPath, path.lstrip('/'))
            print "css path file path is: %s" % cssPath
            if not self.checkPath(cssPath, wwwDirPath):
                return False
            if os.path.exists(cssPath) and os.path.isfile(cssPath):
                # read the file, get the contexts and save it in the response dict
                try:
                    cssFile = open(cssPath)
                    fileContents = cssFile.read()
                    self.responseDict["body"] = fileContents
                    cssFile.close()
                    self.responseDict["return-code"] = "200 OK"
                    self.responseDict["content-type"] = "Content-Type: text/css"
                    return True
                except:
                    return False
            else: # css file doesnt exsist, need to return proper error code
                return False
        # we have enhaused what our server can provide, need to return a failed request back to the client
	# TODO onc last case to catch. Need to handle the case of http://127.0.0.1:8080/deep without the trailing '/'
	# supposed to serve the index.html from that directory
        else:
            # means one of two things. Either the path leads to a directory
            filePath = os.path.join(wwwDirPath, path.lstrip('/'))
            if os.path.exists(filePath) and os.path.isDirectory(filePath):
                # serve the index.html from this file
                pass
            # OR
            # it doesn't exist and we should 404
            else:
                return False

    def checkPath(self, path, basePath):
        if os.path.abspath(path).startswith(basePath):
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

        # form of a good http repsonse
        httpResponse = ""
        httpResponse += "HTTP/1.0 200 OK\r\n"
        httpResponse += "HTTP/1.0 404\r\n"
        httpResponse += "Date: Fri, 31 Dec 1999 23:59:59 GMT\r\n"
        httpResponse += "Content-Type: text/css\r\n"
        httpResponse += "\r\n"
        print httpResponse
        self.request.sendall(httpResponse)
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
        print "http reponse"
        print httpResponse
        return httpResponse

    def build404(self):
        httpResponse = ""
        httpResponse += HTTP_VERSION
        httpResponse += " "
        httpResponse += "404 Not Found"
        httpResponse += END_LINE
        httpResponse += END_LINE
        print "http reponse"
        print httpResponse
        return httpResponse


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
