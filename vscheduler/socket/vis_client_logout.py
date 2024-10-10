import socket, os, platform
from vis_alert import mailFunction

IP1 = "127.0.0.1"   # prod server
IP2 = "127.0.0.2"   # dev server
operating_system = platform.uname()[0]
host = socket.gethostname() # host = platform.uname()[1]
user = os.getlogin()
PORT = 65001
ADDRS = [(IP1, PORT), (IP2, PORT)]
SIZE = 1024
FORMAT = "utf-8"

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    for ADDR in ADDRS:
        connected = True
        try:
            client.connect(ADDR)
        except socket.error as e:
            print (f"Caught exception socket.error: {e}")
            mailFunction(f"socket error - {host}", f"error connecting managment socket server ({ADDR[0]}:{ADDR[1]}) from {host} at LOGOUT attempt for {user}\n{str(e)}")
            os.system(f'pkill -KILL -u {user}')

        print(f"[CONNECTED] VIS CLIENT TO MGMT SERVER AT {ADDR[0]}:{ADDR[0]}")

        while connected:
            msg = [host, user, operating_system]
            client.send((msg[0] + "," + msg[1] + "," + msg[2] + ",logout").encode(FORMAT))
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[MGMT SERVER] sent: {msg}")
            connected = False
        if msg[2] != "dev":
            break

if __name__ == "__main__":
    main()