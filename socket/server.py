import socket
import threading
from vscheduler.modules.cluster.emptypool import empty
from vscheduler.modules.cluster.loadbalance import loadbalance

# IP = socket.gethostbyname(socket.gethostname())
IP = ""
PORT = 65432
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        empty(msg.split("-")[0], msg.split("-")[1])
        loadbalance()
        print(f"[{addr}] {msg}")
        msg = f"Msg received: {msg}"
        conn.send(msg.encode(FORMAT))
        connected = False
    conn.close()

def main():
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()
