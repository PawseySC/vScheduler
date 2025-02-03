# management socket server in charge of managing incoming socket connections from clients for general or booking pools
import socket, threading, subprocess
from tabulate import tabulate
import numpy as np
from vscheduler.general.initiate import PrintCondition
from vscheduler.lib.database import Database
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.log.log import CaptureLog
from vscheduler.modules.cluster.load_balance import loadbalance
from vscheduler.modules.reports.record_log_io import record_login
from vscheduler.modules.reports.record_log_io import record_logout
from vscheduler.modules.guaca.revert_user import revert_back_to_pool
from vscheduler.modules.guaca.empty_pool import empty_pool_connection
from vscheduler.modules.guaca.fill_pool import fillup as fill_up
from vscheduler.modules.guaca.atd import at_daemon
from vscheduler.socket.mgmt_client import client_statistics as data_agent

IP = ""
PORT = 65001
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

socket_records = CaptureLog("server", __file__)
logger = socket_records.log_agent("socket")
# socket_records = CaptureLog("socket", __file__)
# win_logger = socket_records.log_agent("windows")
# linux_logger = socket_records.log_agent("linux")
connection = Database.connect_report_db()

def exception(user, os):
    """
    retreives wall time set for specific user.
    in case no record found for a specific user in database,
    general wall time set in config will be returned.
    """
    try:
        exception_query = f"SELECT user, start, end, wall_time FROM {MyCredentials.report_exception_table} WHERE user = '{user}' AND start = end"
        # print (f"exception_query: {exception_query}") if PrintCondition.fprint else 0
        connection.ping()  # reconnecting mysql in case of connection timed out
        with connection.cursor() as cursor:
            cursor.execute(exception_query)
            exception_results = cursor.fetchall()
            print (f"\n{tabulate(exception_results, headers=['user', 'start', 'end', 'wall_time'])}") if PrintCondition.fprint else 0
            # win_logger.info (f"\n{tabulate(exception_results, headers=['user', 'start', 'end', 'wall_time'])}") if os == "Windows" else linux_logger.info (f"\n{tabulate(exception_results, headers=['user', 'start', 'end', 'wall_time'])}")
            logger.info (f"\nlen(exception_results): {len(exception_results)}\n{tabulate(exception_results, headers=['user', 'start', 'end', 'wall_time'])}")
            # print (f"exception_results: {exception_results}") if PrintCondition.fprint else 0
            # print (f"len(exception_results): {len(exception_results)}") if PrintCondition.fprint else 0
            # win_logger.info (f"exception_results: {exception_results}") if os == "Windows" else linux_logger.info (f"exception_results: {exception_results}")
            # win_logger.info (f"len(exception_results): {len(exception_results)}") if os == "Windows" else linux_logger.info (f"len(exception_results): {len(exception_results)}")
            
        return exception_results[0][3] if len(exception_results) > 0 else MyCredentials.general_pool_wall_time
    except connection.Error as e:
        print (f"error retreiving exceptions from < {MyCredentials.report_exception_table} > table\n{e}") if PrintCondition.fprint else 0
        # win_logger.error (f"error retreiving exceptions from < {MyCredentials.report_exception_table} > table\n{e}") if os == "Windows" else linux_logger.error (f"error retreiving exceptions from < {MyCredentials.report_exception_table} > table\n{e}")
        logger.error (f"error retreiving exceptions from < {MyCredentials.report_exception_table} > table\n{e}")
    
    
def check_status(os):
    try:
        sentence = []
        status_query = f"SELECT node, status, start, end FROM {MyCredentials.report_status_table} WHERE start = end"
        # win_logger.info (f"status_query: {status_query}") if os == "windows" else linux_logger.info (f"status_query: {status_query}") 
        logger.info (f"status_query: {status_query}")
        connection.ping()  # reconnecting mysql in case of connection timed out
        connection.commit()  # This commit accepts the inserts by the other session
        with connection.cursor() as cursor:
            cursor.execute(status_query)
            status_results = cursor.fetchall()
        # for row_status in status_results:
        #     node_name = row_status[0]
        #     node_status = row_status[1]
        #     status_start = row_status[2]
        #     status_end = row_status[3]
        #     sentence.insert(len(sentence), [node_name , node_status, status_start, status_end])
        # print ("\n", tabulate(sentence, headers=['node', 'status', 'start', 'end'])) if PrintCondition.fprint else 0
        # win_logger.info ("\n" + tabulate(sentence, headers=['node', 'status', 'start', 'end'])) if os == "windows" else linux_logger.info ("\n" + tabulate(sentence, headers=['node', 'status', 'start', 'end']))
        print (f"\n{tabulate(status_results, headers=['node', 'status', 'start', 'end'])}") if PrintCondition.fprint else 0
        # win_logger.info (f"\n{tabulate(status_results, headers=['node', 'status', 'start', 'end'])}") if os == "windows" else linux_logger.info (f"\n{tabulate(status_results, headers=['node', 'status', 'start', 'end'])}")
        logger.info (f"\n{tabulate(status_results, headers=['node', 'status', 'start', 'end'])}")
        print (f"status nodes: {status_results}") if PrintCondition.fprint else 0
        print (f"len(status_results): {len(status_results)}") if PrintCondition.fprint else 0
        # win_logger.info (f"status nodes: {status_results}") if os == "windows" else linux_logger.info (f"status nodes: {status_results}")
        logger.info (f"status nodes: {status_results}")
        # win_logger.info (f"len(status_results): {len(status_results)}") if os == "windows" else linux_logger.info (f"len(status_results): {len(status_results)}")
        logger.info (f"len(status_results): {len(status_results)}")
        
        return status_results if len(status_results) > 0 else 0
    except connection.Error as e:
        print (f"error retreiving nodes status from < {MyCredentials.report_status_table} > table\n{e}") if PrintCondition.fprint else 0
        # win_logger.error (f"error retreiving node status from < {MyCredentials.report_status_table} > table\n{e}") if os == "windows" else linux_logger.error (f"error retreiving node status from < {MyCredentials.report_status_table} > table\n{e}")
        logger.error (f"error retreiving node status from < {MyCredentials.report_status_table} > table\n{e}")
    
    
# return list of production nodes which are functional
def generate_general_partition_hosts(os, node):
    hosts = []
    if os == "linux":
        # for i in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1):
        #     host = MyCredentials.linux_node_name + "0" + i if i < 10 else MyCredentials.linux_node_name + i
        #     if host not in exception_results:
        #         print (f"linux node < {host} > not in exception list") if PrintCondition.fprint else 0
        #         logger.info (f"linux node < {host} > not in exception list")
        #         hosts.append(host)
        hosts = [MyCredentials.linux_node_name + "0" + str(i) if i < 10 else MyCredentials.linux_node_name + str(i) for i in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1)]
    elif os == "windows":
        # for i in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1):
        #     host = MyCredentials.windows_node_name + "0" + i if i < 10 else MyCredentials.windows_node_name + i
        #     if host not in exception_results:
        #         print (f"windows node < {host} > not in exception list") if PrintCondition.fprint else 0
        #         logger.info (f"windows node < {host} > not in exception list")
        #         hosts.append(host)
        hosts = [MyCredentials.windows_node_name + "0" + str(i) if i < 10 else MyCredentials.windows_node_name + str(i) for i in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1)]
    status_results = check_status(os)
    hosts = [x for x in hosts if x not in np.array(status_results)[:,0]] if status_results != 0 else hosts
    # win_logger.info (f"hosts: {hosts}") if os == "windows" else linux_logger.info (f"hosts: {hosts}")
    logger.info (f"hosts: {hosts}")
    return hosts


def manage_pool(msg, node, user, walltime, os):
    # 1. empty pool by removing connected node from general pool in guaca
    # win_logger.info (f"step 1/5: Empty pool by replacing < {node} > with next available node") if os == "windows" else linux_logger.info (f"step 1/5: Empty pool by replacing < {node} > with next available node")
    logger.info (f"step 1/5: Empty pool by replacing < {node} > with next available node")
    empty_pool_connection(msg.split(",")[0], msg.split(",")[1], MyCredentials.linux_pool) if os == "linux" else empty_pool_connection(msg.split(",")[0], msg.split(",")[1], MyCredentials.windows_pool)

    # 2. trigger valloc to make user member of connected node in guaca by assigning static url
    # win_logger.info (f"step 2/5: Assigning < {user} > to < {node} > through valloc") if os == "windows" else linux_logger.info (f"step 2/5: Assigning < {user} > to < {node} > through valloc")
    logger.info (f"step 2/5: Assigning < {user} > to < {node} > through valloc")
    subprocess.run(['valloc', '-n', node, '-u', user, '-v'])

    # 3. record login time
    # win_logger.info (f"step 3/5: Recording < {user} > login time to < {node} >") if os == "windows" else linux_logger.info (f"step 3/5: Recording < {user} > login time to < {node} >")
    logger.info (f"step 3/5: Recording < {user} > login time to < {node} >")
    record_login(user, node, MyCredentials.report_linux_table, "general") if os == "linux" else record_login(user, node, MyCredentials.report_windows_table, "general")
    
    # 4. set `at` command to kill user's session at wall-time
    at_daemon(user, node, MyCredentials.report_linux_table, walltime)
    
    # 5. fill up pool by new member
    # 5.a. load balance ON -> call mgmt_client to collect usage data from vis nodes to rank those for loadbalance
    # win_logger.info ("step 5/5: load balance/pool fill up") if os == "windows" else linux_logger.info ("step 5/5: load balance/pool fill up")
    logger.info ("step 5/5: load balance/pool fill up")
    if MyCredentials.load_balance:
        # win_logger.warning ("load_balance = TRUE") if os == "windows" else linux_logger.warning ("load_balance = TRUE")
        logger.warning ("load_balance = TRUE")
        hosts = generate_general_partition_hosts(os, node)
        usage_data = data_agent(hosts, os)
        # win_logger.info (f"Usage data obtained from accessible nodes: {usage_data}") if os == "windows" else linux_logger.info (f"Usage data obtained from accessible nodes: {usage_data}")
        logger.info (f"Usage data obtained from accessible nodes: {usage_data}")
        # win_logger.info (f"{os} nodes load balancing in < {MyCredentials.windows_pool} >") if os == "windows" else linux_logger.info (f"{os} nodes load balancing in < {MyCredentials.linux_pool} >")
        logger.info (f"{os} nodes load balancing in < {MyCredentials.windows_pool} >")
        loadbalance(usage_data, MyCredentials.linux_pool) if os == "linux" else loadbalance(usage_data, MyCredentials.windows_pool)
    # 5.b. load balance OFF -> fill up pool with next node in order
    else:
        # win_logger.warning ("load_balance = FALSE") if os == "windows" else linux_logger.warning ("load_balance = FALSE")
        logger.warning ("load_balance = FALSE")
        hosts = generate_general_partition_hosts(os, node)
        fill_up(node, hosts)


def handle_client(conn, addr):
    # win_logger.info (f"[NEW VIS NODE CONNECTION TO MGMT] {addr}")
    logger.info (f"[NEW VIS NODE CONNECTION TO MGMT] {addr}")
    # linux_logger.info (f"[NEW VIS NODE CONNECTION TO MGMT] {addr}")
    logger.info (f"[NEW VIS NODE CONNECTION TO MGMT] {addr}")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        # win_logger.info (f"MSG FROM VIS NODE: {msg.split(',')}") if MyCredentials.windows_node_name in msg else linux_logger.info (f"MSG FROM VIS NODE: {msg.split(',')}")
        logger.info (f"MSG FROM VIS NODE: {msg.split(',')}")
        node = msg.split(",")[0]
        user = msg.split(",")[1]
        operating_system = msg.split(",")[2]

        excepted_walltime = exception(user, operating_system)
        node_status = 'up'
        node_status_lists = check_status(operating_system)
        if len(node_status_lists) != 0:
            for node_status_list in node_status_lists:
                if node in node_status_list:
                    node_status = node_status_list[1]
                
        # print (f"user, excepted_walltime, node_status ::: {user}, {excepted_walltime}, {node_status}")
                
        if node_status != "dev":
            # check if the socket connection request comes from windows nodes
            if MyCredentials.windows_node_name in node: 
                # if windows general partition -> empty windows general pool, then, valloc and finally update windows general pool with new node
                if int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1):
                    if "logout" in msg.split(","):
                        # win_logger.info (f"LOGOUT attempt for {user}")
                        logger.info (f"LOGOUT attempt for {user}")
                        revert_back_to_pool(msg.split(",")[1], msg.split(",")[0], MyCredentials.windows_pool)
                        record_logout(user, node, MyCredentials.report_windows_table, "general")
                    else:
                        manage_pool(msg, node, user, excepted_walltime, "windows")
                
                # if windows booking partition -> trigger vmanage at windows login to check booking validity
                elif int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_booking_range[0], MyCredentials.windows_booking_range[1]+1):
                    if "logout" in msg.split(","):
                        # win_logger.info (f"LOGOUT attempt for {user}")
                        logger.info (f"LOGOUT attempt for {user}")
                        record_logout(user, node, MyCredentials.report_windows_table, "booking")
                    else:
                        record_login(user, node, MyCredentials.report_windows_table, "booking")
                        subprocess.run(['vmanage', '-n', node, '-u', user, '-v'])
                        
            
            # check if the socket connection request comes from linux nodes
            if MyCredentials.linux_node_name in node:
                # if linux general partition -> empty linux general pool, then, valloc and finally update linux general pool with new node
                if int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1): 
                    if "logout" in msg.split(","):
                        # linux_logger.info (f"LOGOUT attempt for {user}")
                        logger.info (f"LOGOUT attempt for {user}")
                        # move user back to pool by logging out of node
                        revert_back_to_pool(msg.split(",")[1], msg.split(",")[0], MyCredentials.linux_pool)
                        record_logout(user, node, MyCredentials.report_linux_table, "general")
                    else:
                        # if len(checkpool(node, MyCredentials.pool)):        # if user goes to static url of specific node
                        manage_pool(msg, node, user, excepted_walltime, "linux")
                
                # if linux booking partition -> trigger vmanage at linux login to check booking validity
                elif int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1):
                    if "logout" in msg.split(","):
                        # linux_logger.info (f"LOGOUT attempt for {user}")
                        logger.info (f"LOGOUT attempt for {user}")
                        record_logout(user, node, MyCredentials.report_linux_table, "booking")
                    else:
                        record_login(user, node, MyCredentials.report_linux_table, "booking")
                        subprocess.run(['vmanage', '-n', node, '-u', user, '-v'])
        
        conn.send((user + "," + str(excepted_walltime) + "," + node_status).encode(FORMAT))
        connected = False
    conn.close()




def main():
    # win_logger.info ("[STARTING] MGMT SERVER STARTING...")
    logger.info ("[STARTING] MGMT SERVER STARTING...")
    # linux_logger.info ("[STARTING] MGMT SERVER STARTING...")
    logger.info ("[STARTING] MGMT SERVER STARTING...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    # win_logger.info (f"[LISTENING] MGMT SERVER LISTENING ON {IP}:{PORT}")
    logger.info (f"[LISTENING] MGMT SERVER LISTENING ON {IP}:{PORT}")
    # linux_logger.info (f"[LISTENING] MGMT SERVER LISTENING ON {IP}:{PORT}")
    logger.info (f"[LISTENING] MGMT SERVER LISTENING ON {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        # win_logger.info (f"[ACTIVE CONNECTIONS TO MGMT] {threading.active_count() - 1}")
        logger.info (f"[ACTIVE CONNECTIONS TO MGMT] {threading.active_count() - 1}")
        # linux_logger.info (f"[ACTIVE CONNECTIONS TO MGMT] {threading.active_count() - 1}")
        logger.info (f"[ACTIVE CONNECTIONS TO MGMT] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()