import socket, os, platform
from vis_alert import mailFunction

IP = "127.0.0.1"
operating_system = platform.uname[0]
host = socket.gethostname() # host = platform.uname[1]
user = os.getlogin()
PORT = 65001
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
    except socket.error as e:
        print (f"Caught exception socket.error: {e}")
        mailFunction(f"socket error - {host}", f"error connecting managment socket server ({IP, PORT}) from {host} at LOGIN attempt for {user}\n{str(e)}")
        os.system(f'pkill -KILL -u {user}')

    print(f"[CONNECTED] VIS CLIENT TO MGMT SERVER AT {IP}:{PORT}")
    connected = True
    while connected:
        msg = [host, user, operating_system]
        client.send((msg[0] + "," + msg[1] + "," + msg[2]).encode(FORMAT))
        msg = client.recv(SIZE)
        print(f"[MGMT SERVER] sent: {msg}")
        if msg[4] == "non-admin":
            os.system('echo "/usr/bin/python3 /etc/profile.d/vis_client_logout.py" | at now +8 hour')
            os.system('echo "pkill -9 -u $USER" | at now +481 minute')
        connected = False
        
if __name__ == "__main__":
    main()