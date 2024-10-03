import socket, os, platform, multiprocessing
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


# Process class
class Process(multiprocessing.Process):
    def __init__(self, ip, port):
        super(Process, self).__init__()
        self.ip = ip
        self.port = port
        self.ADDR = [(self.ip, self.port)]
        
    def run(self):
        print ("IP: {}".format(self.ip))
        print ("PORT: {}".format(self.port))
        
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = True
        try:
            client.connect(self.ADDR)
        except socket.error as e:
            print (f"Caught exception socket.error: {e}")
            mailFunction(f"socket error - {host}", f"error connecting managment socket server ({self.ADDR[0]}:{self.ADDR[1]}) from {host} at LOGIN attempt for {user}\n{str(e)}")
            os.system(f'pkill -KILL -u {user}')

        print(f"[CONNECTED] VIS CLIENT TO MGMT SERVER AT {self.ADDR[0]}:{self.ADDR[1]}")
        
        while connected:
            msg = [host, user, operating_system]
            client.send((msg[0] + "," + msg[1] + "," + msg[2]).encode(FORMAT))
            msg = client.recv(SIZE)
            print(f"[MGMT SERVER] sent: {msg}")
            if msg[2] == "up":
                os.system(f'echo "/usr/bin/python3 /etc/profile.d/vis_client_logout.py" | at now +{msg[1]} hour')
                os.system(f'echo "pkill -9 -u $USER" | at now +{msg[1] + 1} minute')
            connected = False
        # if msg[2] != "dev":
        #     break
        
        
def main():    
    for ADDR in ADDRS:
        p = Process(ADDR[0], ADDR[1])
        p.start()       # Create a new process and invoke the Process.run() method
        p.join()        # Process.join() to wait for task completion
        
        
if __name__ == "__main__":
    main()