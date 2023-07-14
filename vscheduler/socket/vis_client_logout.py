import socket, os

IP = "127.0.0.1"
host = socket.gethostname()
user = os.getlogin()
PORT = 65001
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
exception = ["admin"]

def main():
    if user not in exception:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        print(f"[CONNECTED] VIS CLIENT TO MGMT SERVER AT {IP}:{PORT}")

        connected = True
        while connected:
            msg = [host, user]
            client.send((msg[0] + "," + msg[1] + ",logout").encode(FORMAT))
            msg = client.recv(SIZE)
            print(f"[MGMT SERVER] sent: {msg}")
            connected = False
        
if __name__ == "__main__":
    main()