import socket, time, threading, subprocess
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.modules.cluster.emptypool import empty
from vscheduler.modules.cluster.revertuser import revert
from vscheduler.modules.cluster.loadbalance import loadbalance
from vscheduler.modules.cluster.logoff import logoff
from vscheduler.modules.cluster.checkpool import checkpool
from vscheduler.socket.mgmt_client import client_program as data_agent

IP = ""
PORT = 65001
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

def handle_client(conn, addr):
    print(f"[NEW VIS NODE CONNECTION TO MGMT] {addr}")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        print("MSG FROM VIS NODE:", msg.split(","))
        node = msg.split(",")[0]
        user = msg.split(",")[1]

        # triggers vmanage at windows login
        if MyCredentials.windows_node_name in node and node.replace(MyCredentials.windows_node_name, "") in MyCredentials.windows_booking_range:
            subprocess.run(['vmanage', '-n', node, '-u', user, '-v'])
            
        if "logout" in msg.split(","):
            print ("msg.split(",")[1]=>user=>", msg.split(",")[1])
            revert(msg.split(",")[1])
        else:
            if len(checkpool(node, MyCredentials.pool)):        # if user goes to static url of specific node
                # removes connected node from general pool in guaca
                print ("empty now")
                empty(msg.split(",")[0], msg.split(",")[1])

                # put user member of connected node in guaca by triggering valloc 
                print("valloc now")
                subprocess.run(['valloc', '-n', node, '-u', user, '-v'])

                # calls mgmt_client to collect usage data in vis nodes as feed for loadbalance
                usage_data = data_agent()
                print ("usage_data=>", usage_data)
                print ("load balance now")
                loadbalance(usage_data)
            else:
                logoff(user, node)

        conn.send(msg.encode(FORMAT))
        connected = False
    conn.close()

def main():
    print("[STARTING] MGMT SERVER STARTING...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] MGMT SERVER LISTENING ON {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS TO MGMT] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()