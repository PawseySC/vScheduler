# management socket server in charge of managing pool connections and members
import socket, time, threading, subprocess
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.modules.cluster.emptypool import empty
from vscheduler.modules.cluster.revertuser import revert
from vscheduler.modules.cluster.loadbalance import loadbalance
from vscheduler.modules.cluster.logoff import logoff
from vscheduler.modules.cluster.checkpool import checkpool
from vscheduler.socket.mgmt_client import client_program as data_agent
from vscheduler.modules.guaca.fill_pool import fillup as fill_up

IP = ""
PORT = 65001
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

socket_records = Capture_log("socket", __file__)
logger = socket_records.log_agent()

def handle_client(conn, addr):
    logger.info (f"[NEW VIS NODE CONNECTION TO MGMT] {addr}")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        logger.info (f"MSG FROM VIS NODE: {msg.split(',')}")
        node = msg.split(",")[0]
        user = msg.split(",")[1]

        # triggers vmanage at windows login to assign a node to user logging into windows general pool
        if MyCredentials.windows_node_name in node and node.replace(MyCredentials.windows_node_name, "") in MyCredentials.windows_booking_range:
            subprocess.run(['vmanage', '-n', node, '-u', user, '-v'])
            
        # move user back to pool by logging out of node
        if "logout" in msg.split(","):
            logger.info (f"LOGOUT attempt for {user}")
            revert(msg.split(",")[1])
        # executes at login attempts
        else:
            # if len(checkpool(node, MyCredentials.pool)):        # if user goes to static url of specific node
            # removes connected node from general pool in guaca
            logger.info (f"Empty pool by removing {node}")
            empty(msg.split(",")[0], msg.split(",")[1])

            # put user member of connected node in guaca by triggering valloc 
            logger.info (f"Assigning {user} to {node} through valloc")
            subprocess.run(['valloc', '-n', node, '-u', user, '-v'])

            # calls mgmt_client to collect usage data in vis nodes as feed for loadbalance
            if MyCredentials.load_balance:
                logger.warning ("load_balance = TRUE")
                usage_data = data_agent()
                logger.info (f"Usage data obtained from accessible nodes: {usage_data}")
                logger.info ("Load balancing...")
                loadbalance(usage_data)
            else:
                logger.warning ("load_balance = FALSE")
                fill_up(node)
            # else:
            #     print("logging off")
                # logoff(user, node)

        conn.send(msg.encode(FORMAT))
        connected = False
    conn.close()

def main():
    logger.info ("[STARTING] MGMT SERVER STARTING...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    logger.info (f"[LISTENING] MGMT SERVER LISTENING ON {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        logger.info (f"[ACTIVE CONNECTIONS TO MGMT] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()