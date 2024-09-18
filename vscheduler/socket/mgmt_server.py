# management socket server in charge of managing general/booking connections and members
from tabulate import tabulate
import socket, threading, subprocess
import numpy as np
from vscheduler.log.log import Capture_log
from vscheduler.lib.database import Database as MyDatabase
# from vscheduler.general.timer import Brackets as MyBrackets
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.modules.cluster.load_balance import loadbalance
from vscheduler.modules.guaca.fill_pool import fillup as fill_up
from vscheduler.modules.reports.record_log_io import record_login
from vscheduler.modules.reports.record_log_io import record_logout
from vscheduler.modules.guaca.revert_user import revert_back_to_pool
from vscheduler.modules.guaca.empty_pool import empty_pool_connection
from vscheduler.socket.mgmt_client import client_statistics as data_agent

my_connection = MyDatabase.connect_report_db()

IP = ""
PORT = 65001
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

socket_records = Capture_log("socket", __file__)
logger_win = socket_records.log_agent("windows")
logger_unix = socket_records.log_agent("linux")


def is_excepted(user, os):
    try:
        exception_query = f"SELECT user, start, end, wall_time FROM {MyCredentials.report_exception_table} WHERE user = {user} AND start = end"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor:
            my_cursor.execute(exception_query)
            exception_results = my_cursor.fetchall()
            print (f"\n{tabulate(exception_results, headers=['user', 'privilige'])}") if MyPrintCondition.fprint else 0
            logger_win.info (f"\n{tabulate(exception_results, headers=['user', 'privilige'])}") if os == "Windows" else logger_unix.info (f"\n{tabulate(exception_results, headers=['user', 'privilige'])}")
            print (f"exception_results: {exception_results}") if MyPrintCondition.fprint else 0
            print (f"len(exception_results): {len(exception_results)}") if MyPrintCondition.fprint else 0
            logger_win.info (f"exception_results: {exception_results}") if os == "Windows" else logger_unix.info (f"status nodes: {exception_results}")
            logger_win.info (f"len(exception_results): {len(exception_results)}") if os == "Windows" else logger_unix.info (f"len(exception_results): {len(exception_results)}")
            
        return exception_results[0][3] if len(exception_results) > 0 else MyCredentials.general_pool_wall_time
    except my_connection.Error as e:
        print (f"error retreiving exceptions from < {MyCredentials.report_exception_table} > table\n{e}") if MyPrintCondition.fprint else 0
        logger_win.error (f"error retreiving exceptions from < {MyCredentials.report_exception_table} > table\n{e}") if os == "Windows" else logger_unix.error (f"error retreiving exceptions from < {MyCredentials.report_exception_table} > table\n{e}")
    
    
def check_status(os):
    try:
        sentence = []
        status_query = f"SELECT node, status, start, end FROM {MyCredentials.report_status_table} WHERE start = end"
        logger_win.info (f"status_query: {status_query}") if os == "windows" else logger_unix.info (f"status_query: {status_query}") 
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor:
            my_cursor.execute(status_query)
            status_results = my_cursor.fetchall()
        # for row_status in status_results:
        #     node_name = row_status[0]
        #     node_status = row_status[1]
        #     status_start = row_status[2]
        #     status_end = row_status[3]
        #     sentence.insert(len(sentence), [node_name , node_status, status_start, status_end])
        # print ("\n", tabulate(sentence, headers=['node', 'status', 'start', 'end'])) if MyPrintCondition.fprint else 0
        # logger_win.info ("\n" + tabulate(sentence, headers=['node', 'status', 'start', 'end'])) if os == "windows" else logger_unix.info ("\n" + tabulate(sentence, headers=['node', 'status', 'start', 'end']))
        print (f"\n{tabulate(status_results, headers=['node', 'status', 'start', 'end'])}") if MyPrintCondition.fprint else 0
        logger_win.info (f"\n{tabulate(status_results, headers=['node', 'status', 'start', 'end'])}") if os == "windows" else logger_unix.info (f"\n{tabulate(status_results, headers=['node', 'status', 'start', 'end'])}")
        print (f"status nodes: {status_results}") if MyPrintCondition.fprint else 0
        print (f"len(status_results): {len(status_results)}") if MyPrintCondition.fprint else 0
        logger_win.info (f"status nodes: {status_results}") if os == "windows" else logger_unix.info (f"status nodes: {status_results}")
        logger_win.info (f"len(status_results): {len(status_results)}") if os == "windows" else logger_unix.info (f"len(status_results): {len(status_results)}")
        
        return status_results
    except my_connection.Error as e:
        print (f"error retreiving nodes status from < {MyCredentials.report_status_table} > table\n{e}") if MyPrintCondition.fprint else 0
        logger_win.error (f"error retreiving node status from < {MyCredentials.report_status_table} > table\n{e}") if os == "windows" else logger_unix.error (f"error retreiving node status from < {MyCredentials.report_status_table} > table\n{e}")
    
    
# return list of production nodes which are functional
def generate_general_partition_hosts(os, node):
    hosts = []
    if os == "linux":
        # for i in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1):
        #     host = MyCredentials.linux_node_name + "0" + i if i < 10 else MyCredentials.linux_node_name + i
        #     if host not in exception_results:
        #         print (f"linux node < {host} > not in exception list") if MyPrintCondition.fprint else 0
        #         logger.info (f"linux node < {host} > not in exception list")
        #         hosts.append(host)
        hosts = [MyCredentials.linux_node_name + "0" + str(i) if i < 10 else MyCredentials.linux_node_name + str(i) for i in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1)]
    elif os == "windows":
        # for i in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1):
        #     host = MyCredentials.windows_node_name + "0" + i if i < 10 else MyCredentials.windows_node_name + i
        #     if host not in exception_results:
        #         print (f"windows node < {host} > not in exception list") if MyPrintCondition.fprint else 0
        #         logger.info (f"windows node < {host} > not in exception list")
        #         hosts.append(host)
        hosts = [MyCredentials.windows_node_name + "0" + str(i) if i < 10 else MyCredentials.windows_node_name + str(i) for i in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1)]
    status_results = check_status(os)
    hosts = [x for x in hosts if x not in np.array(status_results)[:,0]] if len(status_results) > 0 else hosts
    logger_win.info (f"hosts: {hosts}") if os == "windows" else logger_unix.info (f"hosts: {hosts}")
    return hosts


def manage_pool(msg, node, user, os):
    # 1. empty pool by removing connected node from general pool in guaca
    logger_win.info (f"step 1/4: Empty pool by replacing < {node} > with next available node") if os == "windows" else logger_unix.info (f"step 1/4: Empty pool by replacing < {node} > with next available node")
    empty_pool_connection(msg.split(",")[0], msg.split(",")[1], MyCredentials.linux_pool) if os == "linux" else empty_pool_connection(msg.split(",")[0], msg.split(",")[1], MyCredentials.windows_pool)

    # 2. trigger valloc to make user member of connected node in guaca by assigning static url
    logger_win.info (f"step 2/4: Assigning < {user} > to < {node} > through valloc") if os == "windows" else logger_unix.info (f"step 2/4: Assigning < {user} > to < {node} > through valloc")
    subprocess.run(['valloc', '-n', node, '-u', user, '-v'])

    # 3. record login time
    logger_win.info (f"step 3/4: Recording < {user} > login time to < {node} >") if os == "windows" else logger_unix.info (f"step 3/4: Recording < {user} > login time to < {node} >")
    record_login(user, node, MyCredentials.report_linux_table, "general") if os == "linux" else record_login(user, node, MyCredentials.report_windows_table, "general")
    
    # 4. fill up pool by new member
    # 4.a. load balance ON -> call mgmt_client to collect usage data from vis nodes to rank those for loadbalance
    logger_win.info ("step 4/4: load balance/pool fill up") if os == "windows" else logger_unix.info ("step 4/4: load balance/pool fill up")
    if MyCredentials.load_balance:
        logger_win.warning ("load_balance = TRUE") if os == "windows" else logger_unix.warning ("load_balance = TRUE")
        hosts = generate_general_partition_hosts(os, node)
        usage_data = data_agent(hosts, os)
        logger_win.info (f"Usage data obtained from accessible nodes: {usage_data}") if os == "windows" else logger_unix.info (f"Usage data obtained from accessible nodes: {usage_data}")
        logger_win.info (f"{os} nodes load balancing in < {MyCredentials.windows_pool} >") if os == "windows" else logger_unix.info (f"{os} nodes load balancing in < {MyCredentials.linux_pool} >")
        loadbalance(usage_data, MyCredentials.linux_pool) if os == "linux" else loadbalance(usage_data, MyCredentials.windows_pool)
    # 4.b. load balance OFF -> fill up pool with next node in order
    else:
        logger_win.warning ("load_balance = FALSE") if os == "windows" else logger_unix.warning ("load_balance = FALSE")
        hosts = generate_general_partition_hosts(os, node)
        fill_up(node, hosts)


def handle_client(conn, addr):
    logger_win.info (f"[NEW VIS NODE CONNECTION TO MGMT] {addr}")
    logger_unix.info (f"[NEW VIS NODE CONNECTION TO MGMT] {addr}")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        logger_win.info (f"MSG FROM VIS NODE: {msg.split(',')}") if MyCredentials.windows_node_name in msg else logger_unix.info (f"MSG FROM VIS NODE: {msg.split(',')}")
        node = msg.split(",")[0]
        user = msg.split(",")[1]
        operating_system = msg.split(",")[2]

        
        # check if the socket connection request comes from windows nodes
        if MyCredentials.windows_node_name in node: 
            # if windows general partition -> empty windows general pool, then, valloc and finally update windows general pool with new node
            if int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1):
                if "logout" in msg.split(","):
                    logger_win.info (f"LOGOUT attempt for {user}")
                    revert_back_to_pool(msg.split(",")[1], msg.split(",")[0], MyCredentials.windows_pool)
                    record_logout(user, node, MyCredentials.report_windows_table, "general")
                else:
                    manage_pool(msg, node, user, "windows")
            
            # if windows booking partition -> trigger vmanage at windows login to check booking validity
            elif int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_booking_range[0], MyCredentials.windows_booking_range[1]+1):
                if "logout" in msg.split(","):
                    logger_win.info (f"LOGOUT attempt for {user}")
                    record_logout(user, node, MyCredentials.report_windows_table, "booking")
                else:
                    record_login(user, node, MyCredentials.report_windows_table, "booking")
                    subprocess.run(['vmanage', '-n', node, '-u', user, '-v'])
                    
        
        # check if the socket connection request comes from linux nodes
        if MyCredentials.linux_node_name in node:
            # if linux general partition -> empty linux general pool, then, valloc and finally update linux general pool with new node
            if int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1): 
                if "logout" in msg.split(","):
                    logger_unix.info (f"LOGOUT attempt for {user}")
                    # move user back to pool by logging out of node
                    revert_back_to_pool(msg.split(",")[1], msg.split(",")[0], MyCredentials.linux_pool)
                    record_logout(user, node, MyCredentials.report_linux_table, "general")
                else:
                    # if len(checkpool(node, MyCredentials.pool)):        # if user goes to static url of specific node
                    manage_pool(msg, node, user, "linux")
            
            # if linux booking partition -> trigger vmanage at linux login to check booking validity
            elif int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1):
                if "logout" in msg.split(","):
                    logger_unix.info (f"LOGOUT attempt for {user}")
                    record_logout(user, node, MyCredentials.report_linux_table, "booking")
                else:
                    record_login(user, node, MyCredentials.report_linux_table, "booking")
                    subprocess.run(['vmanage', '-n', node, '-u', user, '-v'])

        conn.send([user, is_excepted(user, operating_system)].encode(FORMAT), check_status(operating_system)[0][1])
        connected = False
    conn.close()




def main():
    logger_win.info ("[STARTING] MGMT SERVER STARTING...")
    logger_unix.info ("[STARTING] MGMT SERVER STARTING...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    logger_win.info (f"[LISTENING] MGMT SERVER LISTENING ON {IP}:{PORT}")
    logger_unix.info (f"[LISTENING] MGMT SERVER LISTENING ON {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        logger_win.info (f"[ACTIVE CONNECTIONS TO MGMT] {threading.active_count() - 1}")
        logger_unix.info (f"[ACTIVE CONNECTIONS TO MGMT] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()