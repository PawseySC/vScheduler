# called by vinfo tool
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.general.timer import Brackets as MyBrackets
from tabulate import tabulate
import pandas as pd
import numpy as np

my_connection = MyDatabase.connect_report_db()

records = Capture_log("status", __file__)
logger = records.log_agent("info")


def print_info():
    try:
        query = f"SELECT node, status, pool from status WHERE start = end"
        with my_connection.cursor() as my_cursor:
            my_cursor.execute(query)
            query_results = my_cursor.fetchall()
        print ("\n", tabulate(query_results, headers=['node', 'status', 'pool'])) if MyPrintCondition.fprint and query_results else 0
        logger.info ("\n" + tabulate(query_results, headers=['node', 'status', 'pool']))
        
        linux_general_hosts = [MyCredentials.linux_node_name + "0" + str(i) if i < 10 else MyCredentials.linux_node_name + str(i) for i in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1)]
        linux_booking_hosts = [MyCredentials.linux_node_name + "0" + str(i) if i < 10 else MyCredentials.linux_node_name + str(i) for i in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1)]
        windows_general_hosts = [MyCredentials.windows_node_name + "0" + str(i) if i < 10 else MyCredentials.windows_node_name + str(i) for i in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1)]
        windows_booking_hosts = [MyCredentials.windows_node_name + "0" + str(i) if i < 10 else MyCredentials.windows_node_name + str(i) for i in range(MyCredentials.linux_booking_range[0], MyCredentials.linux_booking_range[1]+1)]

        sentence = []
        for node in linux_general_hosts:
            if node in np.array(query_results)[:,0]:
                print (f"{node} currently in db")
                sentence.insert(len(sentence), [node , np.array(query_results)[:,0], np.array(query_results)[:,0]])
            else:
                sentence.insert(len(sentence), [node, "idle", pool])
        for node in linux_booking_hosts:
            if node in np.array(query_results)[:,0]:
                print (f"{node} currently in db")
                sentence.insert(len(sentence), [node , np.array(query_results)[:,0], np.array(query_results)[:,0]])
            else:
                sentence.insert(len(sentence), [node, "idle", pool])
        for node in windows_general_hosts:
            if node in np.array(query_results)[:,0]:
                print (f"{node} currently in db")
                sentence.insert(len(sentence), [node , np.array(query_results)[:,0], np.array(query_results)[:,0]])
            else:
                sentence.insert(len(sentence), [node, "idle", pool])
        for node in windows_booking_hosts:
            if node in np.array(query_results)[:,0]:
                print (f"{node} currently in db")
                sentence.insert(len(sentence), [node , np.array(query_results)[:,0], np.array(query_results)[:,0]])
            else:
                sentence.insert(len(sentence), [node, "idle", pool])
        
        print ("\n", tabulate(sentence, headers=['node', 'status', 'pool'])) if MyPrintCondition.fprint and query_results else 0
        logger.info ("\n" + tabulate(sentence, headers=['node', 'status', 'pool']))
                    
    except my_connection.Error as e:
        print (f"status query hit error\n{e}") if MyPrintCondition.fprint else 0
        logger.error (f"status query hit error\n{e}")