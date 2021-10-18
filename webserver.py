####################
# Course: CSE138
# Date: Fall 2021
# Assignment: 1
# Tommaso Framba
# This program implements a simple HTTP interface with specified
# responses to GET and POST requests.
###################

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import os.path
import json
from html.parser import HTMLParser




#handle requests
class helloHandler(BaseHTTPRequestHandler):
    keyValueStore = dict()

    #handle get requests
    def do_GET(self):
        parsed_path = urlparse(self.path).path.split("/")
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':

                #If key exists #200 OK else #404 Not Found
                if parsed_path[2] in self.keyValueStore:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(('{"result": "found", "value": "' + str(self.keyValueStore[parsed_path[2]]) + '"}').encode("utf8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write((r"""{"error": "Key does not exist"}""""").encode("utf8"))

    #handle post requests
    def do_PUT(self):
        parsed_path = urlparse(self.path).path.split("/")
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':

                # Get Json body {"value": <value>}
                content_len = int(self.headers.get('content-length'))
                body = self.rfile.read(content_len)
                data = json.loads(body)

                #400 BAD REQUEST KEY TOO LONG
                if len(parsed_path[2]) > 50:
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write((r"""{"error": "Key is too long"}""""").encode("utf8"))
                #400 BAD REQUEST NO VALUE SPECIFIED
                elif 'value' not in data:
                    self.send_response(400)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write((r"""{"error": "PUT request does not specify a value"}""""").encode("utf8"))
                elif 'value' in data:
                    ##200 OK
                    if parsed_path[2] in self.keyValueStore:
                        self.keyValueStore[parsed_path[2]] = data['value']
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write((r"""{"result": "replaced"}""""").encode("utf8"))
                    ##201 CREATED
                    else:
                        self.send_response(201)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write((r"""{"result": "created"}""""").encode("utf8"))
                        self.keyValueStore[parsed_path[2]] = data['value']

    def do_DELETE(self):
        parsed_path = urlparse(self.path).path.split("/")
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':
                if parsed_path[2] in self.keyValueStore:
                    del self.keyValueStore[parsed_path[2]]
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write((r"""{"result": "deleted"}""""").encode("utf8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write((r"""{"error": "Key does not exist"}""""").encode("utf8"))


#start and run server on port 8090
def main():
    PORT = 8090
    server = HTTPServer(('', PORT), helloHandler)
    print('Server running on port %s' % PORT)
    server.serve_forever()


if __name__ == '__main__':
    main()
