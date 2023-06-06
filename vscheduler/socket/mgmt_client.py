# multiconn-client.py

import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]

hosts = ["127.0.0.1"]
port = 54321

import socket, os, pickle

# IP = socket.gethostbyname(socket.gethostname())
# IP = "127.0.0.1"
IPs = ["127.0.0.1"]
PORT = 54321
# host = socket.gethostname()
# user = os.getlogin()
# ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"

def start_connections():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    connected = True
    for IP in IPs:
        while connected:
        
            ADDR = (IP, PORT)
            client.connect(ADDR)
            print(f"[CONNECTED] MGMT client connected to COMP server at {IP}:{PORT}")
            msg = "mgmt"

            client.send((msg).encode(FORMAT))

            #msg = client.recv(SIZE).decode(FORMAT)
            msg = client.recv(SIZE)
            print(f"[COMP SERVER] sent: {msg}")
            connected = False
# if __name__ == "__main__":
#     start_connections()