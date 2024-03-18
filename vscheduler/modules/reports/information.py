# called by vinfo tool
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.general.timer import Brackets as MyBrackets
from tabulate import tabulate
import pandas as pd
import numpy as np
import pandas

my_connection = MyDatabase.connect_report_db()

records = Capture_log("status", __file__)
logger = records.log_agent("info")

linux_general_hosts = [MyCredentials.linux_node_name + "0" + str(i) if i < 10 else MyCredentials.linux_node_name + str(i) for i in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1)]
linux_booking_hosts = [MyCredentials.linux_node_name + "0" + str(i) if i < 10 else MyCredentials.linux_node_name + str(i) for i in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1)]
windows_general_hosts = [MyCredentials.windows_node_name + "0" + str(i) if i < 10 else MyCredentials.windows_node_name + str(i) for i in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1)]
windows_booking_hosts = [MyCredentials.windows_node_name + "0" + str(i) if i < 10 else MyCredentials.windows_node_name + str(i) for i in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1)]
        

def print_info():
    try:
        query = f"SELECT node, status, pool from status WHERE start = end"
        with my_connection.cursor() as my_cursor:
            my_cursor.execute(query)
            query_results = my_cursor.fetchall()
        print ("\n", tabulate(query_results, headers=['node', 'status', 'pool'], tablefmt='psql')) if MyPrintCondition.fprint and query_results else 0
        logger.info ("\n" + tabulate(query_results, headers=['node', 'status', 'pool'], tablefmt='psql'))
        
        a = np.array(query_results)
        print (f'query_results[np.where(np.array(query_results) == node)[0][1]]: {np.where(a == "setonix-vis05")[0][0]}')
        print (f"linux_general_hosts: {linux_general_hosts}")
        sentence = []
        for node in linux_general_hosts:
            if node in np.array(query_results)[:,0]:
                print (f"{node} currently in db")
                sentence.insert(len(sentence), [node , query_results[np.where(a == node)[0][0]][1], query_results[np.where(a == node)[0][0]][2]])
            else:
                sentence.insert(len(sentence), [node, "idle", "general"])
        for node in linux_booking_hosts:
            if node in np.array(query_results)[:,0]:
                print (f"{node} currently in db")
                sentence.insert(len(sentence), [node , query_results[np.where(a == node)[0][0]][1], query_results[np.where(a == node)[0][0]][2]])
            else:
                sentence.insert(len(sentence), [node, "idle", "booking"])
        for node in windows_general_hosts:
            if node in np.array(query_results)[:,0]:
                print (f"{node} currently in db")
                sentence.insert(len(sentence), [node , query_results[np.where(a == node)[0][0]][1], query_results[np.where(a == node)[0][0]][2]])
            else:
                sentence.insert(len(sentence), [node, "idle", "general"])
        for node in windows_booking_hosts:
            if node in np.array(query_results)[:,0]:
                print (f"{node} currently in db")
                sentence.insert(len(sentence), [node , query_results[np.where(a == node)[0][0]][1], query_results[np.where(a == node)[0][0]][2]])
            else:
                sentence.insert(len(sentence), [node, "idle", "booking"])
        print (f"sentence: {sentence}")
        print ("\n", tabulate(sentence, headers=['node', 'status', 'pool'], tablefmt='psql')) if MyPrintCondition.fprint and query_results else 0
        logger.info ("\n" + tabulate(sentence, headers=['node', 'status', 'pool'], tablefmt='psql'))
                    
    except my_connection.Error as e:
        print (f"status query hit error\n{e}") if MyPrintCondition.fprint else 0
        logger.error (f"status query hit error\n{e}")
        
        
def session (node):
    cluster = MyCredentials.report_linux_table if MyCredentials.linux_node_name in node else MyCredentials.report_windows_table
    query = f"SELECT node, user, pool, start, end from {cluster} WHERE node = '{node}' AND start = end"
    with my_connection.cursor() as my_cursor:
        my_cursor.execute(query)
        query_results = my_cursor.fetchall()
    # print (query, query_results)
    # a = dict(query_results)
    if query_results and (node in linux_general_hosts or node in windows_general_hosts):
        print (f"\nLogged-in Users in < {node} >, {cluster} cluster\n", tabulate(query_results, headers=['node', 'user', 'pool', 'start', 'end'], tablefmt='psql')) if MyPrintCondition.fprint and query_results else 0
        logger.info (f"\nLogged-in Users in < {node} >, {cluster} cluster\n" + tabulate(query_results, headers=['node', 'user', 'pool', 'start', 'end'], tablefmt='psql'))
    else:
        print (f"No one's logged in to < {node} >")
        logger.info (f"No one's logged in to < {node} >")