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

# IMPORTANT: For the exercise sheet, please adhere to the following:
#
#  1.  The main program should be called server.py
#  2.  It should take exactly TWO arguments: <file> <port>, where
#      <file> is the full path to the file with the movie records,
#      and <port> is the port on which the server is listening.

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python3 server.py <file> <port>')
        exit(1)

    input_file = sys.argv[1]
    port = int(sys.argv[2])

    # Create communication socket and listen on port <port>.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((socket.gethostname(), port))
    server.listen(5)

    print('Starting the server at http://%s:%s/' %
          (socket.gethostbyname(socket.gethostname()), port))

    # Server loop.
    while True:
        (client, address) = server.accept()

        # Get the request
        request = client.recv(8192).decode('ascii')
        print('[%s] "GET %s HTTP/1.1"' %
              (time.strftime('%d/%b/%Y %H:%M:%S'),
               re.match(r'^GET (.*) HTTP/1.1', request).group(1)))

        content_type = 'text/plain'

        # Check ...
        match = re.match(r'^GET /(.*) HTTP/1.1', request)
        if match:
            query = match.group(1)
            if query == '':
                query = 'index.html'

            if not re.match(r'/', query):
                if query.startswith('?q='):
                    query = re.match(r'^\?q=(.*)', query).group(1)

                    # TODO: use fuzzy prefix search here
                    content = query
                else:
                    try:
                        with open(query) as file:
                            content = file.read()
                            if query.endswith('.html'):
                                content_type = 'text/html'
                            elif query.endswith('.css'):
                                content_type = 'text/css'
                            elif query.endswith('.js'):
                                content_type = 'application/javascript'
                    except FileNotFoundError:
                        content = ''
            else:
                content = ''

        # Send the response
        if any(content):
            content_length = len(content)
            response = 'HTTP/1.1 200 OK\r\n' \
                       'Content-Length: %d\r\n' \
                       'Content-Type: %s\r\n' \
                       '\r\n%s' % (content_length, content_type, content)
        else:
            response = 'HTTP/1.1 404 Not Found\r\n'

        client.send(response.encode('ascii'))
        client.close()
