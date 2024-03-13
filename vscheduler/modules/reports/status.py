# called by stat tool
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.general.timer import Brackets as MyBrackets
from tabulate import tabulate
import pandas as pd

my_connection = MyDatabase.connect_report_db()

records = Capture_log("status", __file__)
logger_win = records.log_agent("windows")
logger_unix = records.log_agent("linux")


def status_update(node, mode):
    try:
        pool = ""
        sentence = []
        if MyCredentials.windows_node_name in node:
            pool = "GENERAL" if int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1) else "BOOKING"
        elif MyCredentials.linux_node_name in node:
            pool = "GENERAL" if int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1) else "BOOKING"
        
        pre_query = f"SELECT * FROM status WHERE node = '{node}' AND start = end"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor:
            my_cursor.execute(pre_query)
            pre_query_results = my_cursor.fetchall()
        for row_pre_query in pre_query_results:
            node_name = row_pre_query[0]
            node_status = row_pre_query[1]
            node_pool = row_pre_query[2]
            node_start = row_pre_query[3]
            node_end = row_pre_query[4]
            sentence.insert(len(sentence), [node_name, node_status, node_pool, node_start, node_end])
        print (f"no starus record for < {node} > at current time") if MyPrintCondition.fprint and not pre_query_results else 0
        logger_win.info (f"no starus record for < {node} > at current time") if MyCredentials.windows_node_name in node else logger_unix.info (f"no starus record for < {node} > at current time")
        print ("\n", tabulate(sentence, headers=['node', 'status', 'pool', 'start', 'end'])) if MyPrintCondition.fprint and pre_query_results else 0
        logger_win.info ("\n" + tabulate(sentence, headers=['node', 'status', 'pool', 'start', 'end'])) if MyCredentials.windows_node_name in node else logger_unix.info ("\n" + tabulate(sentence, headers=['node', 'status', 'pool', 'start', 'end']))
    except my_connection.Error as e:
        print (f"status record error for node < {node} > in pre_query = {pre_query}\n{e}") if MyPrintCondition.fprint else 0
        logger_win.error (f"status record error for node < {node} > in pre_query = {pre_query}\n{e}") if MyCredentials.windows_node_name in node else logger_unix.error (f"status record error for node < {node} > in pre_query = {pre_query}\n{e}")
    
    # is this logic correct for setting/updating node status?
    # set down -> if no record for current time for current node, insert new record set the status down
    #                       if any current record for current node, update its end time and insert new record with status down
    # set maint ->  if no record for current time for current node, insert new record set the status maint
    #                       if any current record for current node, update its end time and insert new record with status down
    # set up -> only update any current record end time meaning that status is finished and no one using = idle
    # set allocated ->  if no record for current time for current node, insert new record set the status allocated
    #                             if any current record for current node, update its end time and insert new record for status allocated
    # set reserved ->  if no record for current time for current node, insert new record set the status reserved
    #                            if any current record for current node, if status != down and maint, then update its end time and insert new record for status down

    post_query = ""
    if pre_query_results[:][1] != "down" and pre_query_results[:][1] != "maintenance" and mode != "up":
        if not pre_query_results:
            post_query = f"INSERT INTO {MyCredentials.report_status_table} (node, status, pool, start, end) VALUES ('{node}', '{mode}', '{pool}', '{MyBrackets.local_time}', '{MyBrackets.local_time}')"
        elif pre_query_results:
            post_query = f'''
                UPDATE {MyCredentials.report_status_table} SET end = {MyBrackets.local_time} WHERE node = '{node}' AND start = end;
                INSERT INTO {MyCredentials.report_status_table} (node, status, pool, start, end) VALUES ('{node}', '{mode}', '{pool}', '{MyBrackets.local_time}', '{MyBrackets.local_time}')
                '''
    elif mode == "up":
        post_query = f"UPDATE {MyCredentials.report_status_table} SET end = {MyBrackets.local_time} WHERE node = '{node}' AND start = end"
            
    try:
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor:
            my_cursor.execute(post_query)
            my_connection.commit()
        print (f"{my_cursor.rowcount} record(s) inserted into < {MyCredentials.report_status_table} > table") if MyPrintCondition.fprint else 0  
        logger_win.info (f"{my_cursor.rowcount} record(s) inserted into < {MyCredentials.report_status_table} > table") if MyCredentials.windows_node_name in node else logger_unix.info (f"{my_cursor.rowcount} record(s) inserted into < {MyCredentials.report_status_table} > table")
    except my_connection.Error as e:
        print (f"status record error for node < {node} > in post_query = {post_query}\n{e}") if MyPrintCondition.fprint else 0
        logger_win.error (f"status record error for node < {node} > in post_query = {post_query}\n{e}") if MyCredentials.windows_node_name in node else logger_unix.error (f"status record error for node < {node} > in post_query = {post_query}\n{e}")
            
    
    
# def set_status_down(node):
#     pool = ""
#     if MyCredentials.windows_node_name in node:
#         pool = "GENERAL" if int(node.removeprefix(MyCredentials.windows_node_name)) in range(MyCredentials.windows_general_range[0], MyCredentials.windows_general_range[1]+1) else "BOOKING"
#     elif MyCredentials.linux_node_name in node:
#         pool = "GENERAL" if int(node.removeprefix(MyCredentials.linux_node_name)) in range(MyCredentials.linux_general_range[0], MyCredentials.linux_general_range[1]+1) else "BOOKING"
    
#     query = f"INSERT INTO {MyCredentials.report_status_table} (node, status, pool, start, end) VALUES ('{node}', 'down', '{pool}', '{MyBrackets.local_time}', '{MyBrackets.local_time}')"
#     logger_win.info (f"status_query: {query}") if MyCredentials.windows_node_name in node else logger_unix.info (f"status_query: {query}")
#     my_connection.ping()  # reconnecting mysql in case of connection timed out
#     with my_connection.cursor() as my_cursor:
#         my_cursor.execute(query)
#         my_connection.commit()
#     print (f"{my_cursor.rowcount} record(s) inserted into status table") if MyPrintCondition.fprint else 0  
#     logger_win.info (f"{my_cursor.rowcount} record(s) inserted into status table") if MyCredentials.windows_node_name in node else logger_unix.info (f"{my_cursor.rowcount} record(s) inserted into status table")

# def set_status_up(node):
#     query = f"UPDATE {MyCredentials.report_status_table} SET status = 'idle', end = {MyBrackets.local_time} WHERE node = '{node}' AND status = 'down', start = end AND start < {MyBrackets.local_time}"
#     logger_win.info (f"status_query: {query}") if MyCredentials.windows_node_name in node else logger_unix.info (f"status_query: {query}")
#     my_connection.ping()  # reconnecting mysql in case of connection timed out
#     with my_connection.cursor() as my_cursor:
#         my_cursor.execute(query)
#         my_connection.commit()
#     print (f"{my_cursor.rowcount} record(s) updated in status table") if MyPrintCondition.fprint else 0  
#     logger_win.info (f"{my_cursor.rowcount} record(s) updated in status table") if MyCredentials.windows_node_name in node else logger_unix.info (f"{my_cursor.rowcount} record(s) updated in status table")

# def exception_status(node, start, end):
#     query = " WHERE " if node or start or end else 0
#     if query:
#         if node:
#             query = query + f"node = '{node}'"
#             if start:
#                 query = query + f" AND start = '{start}'"
#                 if end:
#                     query = query + f" AND end = '{end}"
#         else:
#             if start:
#                 query = query + f" AND start = '{start}'"
#                 if end:
#                     query = query + f" AND end = '{end}"
#             else:
#                 if end:
#                     query = query + f" AND end = '{end}"

#     print (query)
#     actual_status_query = f"SELECT * FROM {MyCredentials.report_exception_table}" + query
#     actual_status_report_results = pd.read_sql(actual_status_query, my_connection)