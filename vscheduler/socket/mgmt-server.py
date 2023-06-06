#!/home/ubuntu/pool/vs/bin/python
import socket
import threading
import subprocess
from vscheduler.modules.cluster.emptypool import empty
from vscheduler.modules.cluster.loadbalance import loadbalance
from vscheduler.socket.mgmt_client import start_connections as mg

# IP = socket.gethostbyname(socket.gethostname())
IP = ""
PORT = 65432
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"

def handle_client(conn, addr):
    print(f"[NEW CONNECTION to MGMT] {addr} connected from COMP client.")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)

        print("splited:", msg.split("-"))
        node = msg.split("-")[0]
        user = msg.split("-")[1]
        print (msg.split("-")[0])
        print (msg.split("-")[1])
        # empty(msg.split("-")[0], msg.split("-")[1])
        print ("now going to run mg")
        
        mg()
        print ("finished running mg")
        # subprocess.run(['valloc', '-n', node, '-u', user, '-v'])
        # loadbalance()

        print(f"[{addr}] {msg}")
        msg = f"Msg received from client: {msg}"
        # msg = wikipedia.summary(msg, sentences=1)
        conn.send(msg.encode(FORMAT))
        connected = False
    conn.close()

def main():
    print("[STARTING] MGMT Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] MGMT Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS TO MGMT] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()