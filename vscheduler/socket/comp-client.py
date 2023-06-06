import socket, os, pickle

# IP = socket.gethostbyname(socket.gethostname())
IP = "127.0.0.1"
host = socket.gethostname()
user = os.getlogin()
PORT = 65432
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"[CONNECTED] COMP client connected to MGMT server at {IP}:{PORT}")

    connected = True
    while connected:
        msg = [host, user]

        client.send((msg[0]+"-"+msg[1]).encode(FORMAT))

        #msg = client.recv(SIZE).decode(FORMAT)
        msg = client.recv(SIZE)
        print(f"[MGMT SERVER] sent: {msg}")
        connected = False
if __name__ == "__main__":
    main()