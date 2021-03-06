####################
# Course: CSE138
# Date: Fall 2021
# Assignment: 2
# Tommaso Framba
# Eric Yao Huang
# This program implements a simple HTTP interface with specified
# responses to GET and PUT and DELETE requests.
###################

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import os.path
import json
import requests
import socket
import subprocess
from html.parser import HTMLParser

#handle requests
class helloHandler(BaseHTTPRequestHandler):
    keyValueStore = dict()

    #handle get requests
    def do_GET(self):
        parsed_path = urlparse(self.path).path.split("/")
        if len(parsed_path) == 2 and parsed_path[1] == 'kvs': parsed_path.append("") #Handle as if it was empty string
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':

                #If key exists #200 OK else #404 Not Found
                if parsed_path[2] in self.keyValueStore:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = { "result": "found", "value": self.keyValueStore[parsed_path[2]] }
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"error": "Key does not exist"}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))

    #handle post requests
    def do_PUT(self):
        parsed_path = urlparse(self.path).path.split("/")
        if len(parsed_path) == 2 and parsed_path[1] == 'kvs': parsed_path.append("") #Handle as if it was empty string
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':

                # Get Json body {"value": <value>}
                content_len = int(self.headers.get('content-length'))
                body = self.rfile.read(content_len)
                data = json.loads(body)

                #400 BAD REQUEST KEY TOO LONG
                if len(parsed_path[2]) > 50:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"error": "Key is too long"}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))
                #400 BAD REQUEST NO VALUE SPECIFIED
                elif 'value' not in data:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"error": "PUT request does not specify a value"}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))
                elif 'value' in data:
                    ##200 OK
                    if parsed_path[2] in self.keyValueStore:
                        self.keyValueStore[parsed_path[2]] = data['value']
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        jsndict = {"result": "replaced"}
                        jsnrtrn = json.dumps(jsndict)
                        self.wfile.write(jsnrtrn.encode("utf8"))
                    ##201 CREATED
                    else:
                        self.send_response(201)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        jsndict = {"result": "created"}
                        jsnrtrn = json.dumps(jsndict)
                        self.wfile.write(jsnrtrn.encode("utf8"))
                        self.keyValueStore[parsed_path[2]] = data['value']

    def do_DELETE(self):
        parsed_path = urlparse(self.path).path.split("/")
        if len(parsed_path) == 2 and parsed_path[1] == 'kvs': parsed_path.append("") #Handle as if it was empty string
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':
                if parsed_path[2] in self.keyValueStore:
                    del self.keyValueStore[parsed_path[2]]
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"result": "deleted"}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"error": "Key does not exist"}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))

class proxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        
        #get path of the request
        parsed_path = self.path
        url = "http://" + os.environ.get('FORWARDING_ADDRESS') + parsed_path # from your code above

        
        # print("\nparsed_path is: ")
        # print(parsed_path)
        # print("\n url is: ")
        # print(url)

        # test if server is up
        host = str(os.environ.get('FORWARDING_ADDRESS')).split(":")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host[0],int(host[1])))

        # if it is up, forward it
        if result == 0:
            sock.close()
            response = requests.get(url, timeout=2.50)
            print("\nresponse is: ")
            print(response)
            self.send_response(response.status_code)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            jsndict = response.json()
            jsnrtrn = json.dumps(jsndict)
            self.wfile.write(jsnrtrn.encode("utf8"))
        else: # otherwise return 503
            self.send_response(503)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            jsndict = {"error": "Cannot forward request"}
            jsnrtrn = json.dumps(jsndict)
            self.wfile.write(jsnrtrn.encode("utf8"))

        

        

    def do_PUT(self):
        
        #get path of the request
        parsed_path = self.path
        url = "http://" + os.environ.get('FORWARDING_ADDRESS') + parsed_path 

        #get the json body
        content_len = int(self.headers.get('content-length'))
        body = self.rfile.read(content_len)
        data = json.loads(body)

        
        
        # print("\nparsed_path is: ")
        # print(parsed_path)
        # print("\n url is: ")
        # print(url)

        # test is server up
        host = str(os.environ.get('FORWARDING_ADDRESS')).split(":")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host[0],int(host[1])))

        # if up, forward
        if result == 0:
            sock.close()
            response = requests.put(url, json = data, timeout=2.50)
            print("\nresponse is: ")
            print(response)
            self.send_response(response.status_code)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            jsndict = response.json()
            jsnrtrn = json.dumps(jsndict)
            self.wfile.write(jsnrtrn.encode("utf8"))
        else: # else return 503
            self.send_response(503)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            jsndict = {"error": "Cannot forward request"}
            jsnrtrn = json.dumps(jsndict)
            self.wfile.write(jsnrtrn.encode("utf8"))
        

    def do_DELETE(self):
        
        # get path of request
        parsed_path = self.path
        url = "http://" + os.environ.get('FORWARDING_ADDRESS') + parsed_path # from your code above

        # print("\nparsed_path is: ")
        # print(parsed_path)
        # print("\n url is: ")
        # print(url)

        # test is server up
        host = str(os.environ.get('FORWARDING_ADDRESS')).split(":")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host[0],int(host[1])))

        # if up forward it
        if result == 0:
            sock.close()
            response = requests.delete(url, timeout=2.50)
            print("\nresponse is: ")
            print(response)
            self.send_response(response.status_code)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            jsndict = response.json()
            jsnrtrn = json.dumps(jsndict)
            self.wfile.write(jsnrtrn.encode("utf8"))
        else: # else return 503
            self.send_response(503)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            jsndict = {"error": "Cannot forward request"}
            jsnrtrn = json.dumps(jsndict)
            self.wfile.write(jsnrtrn.encode("utf8"))


    
    

    

#start and run server on port 8090
def main():
    if os.environ.get('FORWARDING_ADDRESS') == None:
        PORT = 8090
        server = HTTPServer(('', PORT), helloHandler)
        
        print('Server running on port %s' % PORT)
        
        server.serve_forever()
    else:
        PORT = 8090
        server = HTTPServer(('', PORT), proxyHandler)
        
        print('Proxy running on port %s' % PORT)
        
        server.serve_forever()


if __name__ == '__main__':
    main()
