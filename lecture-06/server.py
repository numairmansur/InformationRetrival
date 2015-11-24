"""
Copyright 2015, University of Freiburg.
Chair of Algorithms and Data Structures.
Hannah Bast <bast@cs.uni-freiburg.de>
"""

import socket
import time
import sys

# Demo search server
#
# IMPORTANT: For the exercise sheet, please adhere to the following:
#
#  1.  The main program should be called server.py
#  2.  It should take exactly TWO arguments: <file> <port>, where
#      <file> is the full path to the file with the movie records,
#      and <port> is the port on which the server is listening.
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 server.py <file> <port>")
        exit(1)
    input_file = sys.argv[1]
    port = int(sys.argv[2])
    # Create communication socket and listen on port 80.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((socket.gethostname(), port))
    server.listen(5)
    # Server loop.
    while True:
        print("\x1b[1mWaiting for requests on port %d ... \x1b[0m" % port)
        (client, address) = server.accept()
        print("Incoming request at " + time.ctime())
        result = "Not now, honey!"
        print("Sending result: " + result)
        message = client.recv(1 << 31).decode("ascii")
        client.send(result.encode("ascii"))
        client.close()
