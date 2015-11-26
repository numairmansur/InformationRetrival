"""
Copyright 2015, University of Freiburg.
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
Evgeny Anatskiy <evgeny.anatskiy@jupiter.uni-freiburg.de>
Numair Mansur <numair.mansur@gmail.com>
"""

import socket
import time
import sys
import re
import json
from urllib.request import unquote

from qgram_index import QgramIndex


class Server:
    """ :) """

    def __init__(self, port):
        self.port = port

        # Create communication socket and listen on port <port>.
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((socket.gethostname(), port))
        self.server.listen(5)

    def accept(self):
        return self.server.accept()

    def get_address(self):
        return 'http://' + socket.gethostbyname(socket.gethostname()) + ':' + \
               str(self.port) + '/'


class Response:
    """ :) """

    def __init__(self):
        self.content_type = 'text/plain'
        self.content = ''

    def set_content_type(self, file):
        if file.endswith('.html'):
            self.content_type = 'text/html'
        elif file.endswith('.css'):
            self.content_type = 'text/css'
        elif file.endswith('.js'):
            self.content_type = 'application/javascript'

    def get_hits(self, qi, query):
        normalized_query = re.sub('\W+', '', unquote(query)).lower()
        delta = len(normalized_query) // 4

        hits = qi.find_matches(normalized_query, delta)
        result = [{'title': hit[0], 'year': hit[1]} for hit in hits]

        return json.dumps(result)

    def set_content(self, request, qi):
        match = re.match(r'^GET /(.*) HTTP/1.1', request)
        if match:
            query = match.group(1)
            if query == '':
                query = 'index.html'

            if not re.match(r'/', query):
                if query.startswith('?q='):
                    query = re.match(r'^\?q=(.*)', query).group(1)
                    self.content = self.get_hits(qi, query)
                else:
                    # File is requested
                    try:
                        with open(query) as file:
                            self.content = file.read()
                            self.set_content_type(query)
                    except FileNotFoundError:
                        self.content = ''
            else:
                self.content = ''

    def get_response(self):
        if any(self.content):
            content_length = len(self.content)
            res = 'HTTP/1.1 200 OK\r\n' \
                  'Content-Length: %d\r\n' \
                  'Content-Type: %s\r\n' \
                  '\r\n%s' % (content_length, self.content_type, self.content)
        else:
            res = 'HTTP/1.1 404 Not Found\r\n'
        return res.encode('ascii')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 server.py <file> <port>')
        exit(1)

    input_file = sys.argv[1]
    port = int(sys.argv[2])

    # Reading the movies file
    print('Loading movies file...')
    qi = QgramIndex(3)
    qi.read_from_file(input_file)

    # Create Server object
    server = Server(port)
    print('Starting the server at ' + server.get_address())

    # Server loop.
    while True:
        (client, address) = server.accept()

        # Get the request
        request = client.recv(8192).decode('ascii')
        print('[%s] "GET %s HTTP/1.1"' %
              (time.strftime('%d/%b/%Y %H:%M:%S'),
               re.match(r'^GET (.*) HTTP/1.1', request).group(1)))

        # Send the response
        response = Response()
        response.set_content(request, qi)
        client.send(response.get_response())
        client.close()
