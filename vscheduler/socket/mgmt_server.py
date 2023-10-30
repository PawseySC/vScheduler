# management socket server in charge of managing pool connections and members
import socket, time, threading, subprocess
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.modules.guaca.empty_pool import empty
from vscheduler.modules.guaca.revert_user import revert
from vscheduler.modules.cluster.load_balance import loadbalance
from vscheduler.modules.cluster.log_off import logoff
from vscheduler.modules.guaca.check_pool import checkpool
from vscheduler.socket.mgmt_client import client_program as data_agent
from vscheduler.modules.guaca.fill_pool import fillup as fill_up
from vscheduler.modules.reports.record_log_io import record_login
from vscheduler.modules.reports.record_log_io import record_logout

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
        if MyCredentials.windows_node_name in node: 
            if int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_booking_range[1]+1):
                if "logout" in msg.split(","):
                    record_logout(user, node, MyCredentials.report_windows_table, "general")
                else:
                    # subprocess.run(['vmanage', '-n', node, '-u', user, '-v'])
                    record_login(user, node, MyCredentials.report_windows_table, "general")
            
            elif int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_booking_range[0], MyCredentials.windows_booking_range[1]+1):
                if "logout" in msg.split(","):
                    record_logout(user, node, MyCredentials.report_windows_table, "booking")
                else:
                    record_login(user, node, MyCredentials.report_windows_table, "booking")
                    subprocess.run(['vmanage', '-n', node, '-u', user, '-v'])
                    

        if MyCredentials.linux_node_name in node and int(node.replace(MyCredentials.linux_node_name, "")) in MyCredentials.linux_general_range: 
            # move user back to pool by logging out of node
            if "logout" in msg.split(","):
                logger.info (f"LOGOUT attempt for {user}")
                revert(msg.split(",")[1])
                record_logout(user, node, MyCredentials.report_linux_table, "general")
            # executes at login attempts
            else:
                # if len(checkpool(node, MyCredentials.pool)):        # if user goes to static url of specific node
                # removes connected node from general pool in guaca
                logger.info (f"Empty pool by removing {node}")
                empty(msg.split(",")[0], msg.split(",")[1])

                # put user member of connected node in guaca by triggering valloc 
                logger.info (f"Assigning {user} to {node} through valloc")
                subprocess.run(['valloc', '-n', node, '-u', user, '-v'])

                # record login time
                record_login(user, node, MyCredentials.report_linux_table, "general")
                
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