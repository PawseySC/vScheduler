from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib import config
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.general.timer import Brackets as MyBrackets
from vscheduler.modules.guaca.pool_refresh import refresh
from tabulate import tabulate
import pandas as pd
import numpy as np

my_connection = MyDatabase.connect_report_db()

status_records = CaptureLog("status", __file__)
logger = status_records.log_agent("reports")


def status_update(node, mode):
    """
    Called by stat tool
    """
    try:
        pool = post_query = ""
        sentence = []
        if config.partition['windows']['node'] in node:
            pool = "general" if int(node.removeprefix(config.partition['windows']['node'])) in range(config.partition['windows']['general']['range'][0], config.partition['windows']['general']['range'][1]+1) else "reservation"
        elif config.partition['linux']['node'] in node:
            pool = "general" if int(node.removeprefix(config.partition['linux']['node'])) in range(config.partition['linux']['general']['range'][0], config.partition['linux']['general']['range'][1]+1) else "reservation"
        
        pre_query = f"SELECT node, status, pool, start, end FROM status WHERE node = '{node}' AND start = end"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor:
            my_cursor.execute(pre_query)
            pre_query_results = my_cursor.fetchall()
        # if len(pre_query_results) == 0:
            # for row_pre_query in pre_query_results:
            #     node_name = row_pre_query[1]
            #     node_status = row_pre_query[2]
            #     node_pool = row_pre_query[3]
            #     node_start = row_pre_query[4]
            #     node_end = row_pre_query[5]
            #     sentence.insert(len(sentence), [node_name, node_status, node_pool, node_start, node_end])
            # print (f"no starus record for < {node} > at current time") if MyPrintCondition.fprint and not pre_query_results else 0
            # logger_win.info (f"no starus record for < {node} > at current time") if config.partition['windows']['node'] in node else logger_unix.info (f"no starus record for < {node} > at current time")
        if len(pre_query_results) > 0:
            print ("\n", tabulate(pre_query_results, headers=['node', 'status', 'pool', 'start', 'end'])) if MyPrintCondition.fprint and pre_query_results else 0
            # logger_win.info ("\n" + tabulate(pre_query_results, headers=['node', 'status', 'pool', 'start', 'end'])) if config.partition['windows']['node'] in node else logger_unix.info ("\n" + tabulate(pre_query_results, headers=['node', 'status', 'pool', 'start', 'end']))
            logger.info ("\n" + tabulate(pre_query_results, headers=['node', 'status', 'pool', 'start', 'end']))
            if mode != "up":
                post_query = [f"UPDATE {config.database['report']['table']['status']} SET end = '{MyBrackets.local_time}' WHERE node = '{node}' AND start = end",
                    f"INSERT INTO {config.database['report']['table']['status']} (node, status, pool, start, end) VALUES ('{node}', '{mode}', '{pool}', '{MyBrackets.local_time}', '{MyBrackets.local_time}')"] if mode not in np.array(pre_query_results)[:,1] else 0
            else:
                post_query = [f"UPDATE {config.database['report']['table']['status']} SET end = '{MyBrackets.local_time}' WHERE node = '{node}' AND start = end"]
        else:
            print (f"No status record for < {node} > at current time meaning it's idle") if MyPrintCondition.fprint else 0
            # logger_win.info (f"No status record for < {node} > at current time meaning it's idle") if config.partition['windows']['node'] in node else logger_unix.info (f"No status record for < {node} > at current time meaning it's idle")
            logger.info (f"No status record for < {node} > at current time meaning it's idle")
            post_query = [f"INSERT INTO {config.database['report']['table']['status']} (node, status, pool, start, end) VALUES ('{node}', '{mode}', '{pool}', '{MyBrackets.local_time}', '{MyBrackets.local_time}')"] if mode != "up" else 0 #f"UPDATE {config.database['report']['table']['status']} SET end = '{MyBrackets.local_time}' WHERE node = '{node}' AND start = end"
    except my_connection.Error as e:
        print (f"status record error for node < {node} > in pre_query = {pre_query}\n{e}") if MyPrintCondition.fprint else 0
        # logger_win.error (f"status record error for node < {node} > in pre_query = {pre_query}\n{e}") if config.partition['windows']['node'] in node else logger_unix.error (f"status record error for node < {node} > in pre_query = {pre_query}\n{e}")
        logger.error (f"status record error for node < {node} > in pre_query = {pre_query}\n{e}")
    # print ("yes") if mode in np.array(pre_query_results)[:,1] else print ("no")
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

    
    # if "down" not in pre_query_results and "maint" not in pre_query_results and mode != "up":
    #     if not pre_query_results:
    #         post_query = f"INSERT INTO {config.database['report']['table']['status']} (node, status, pool, start, end) VALUES ('{node}', '{mode}', '{pool}', '{MyBrackets.local_time}', '{MyBrackets.local_time}')"
    #     elif pre_query_results:
    #         post_query = f'''
    #             UPDATE {config.database['report']['table']['status']} SET end = '{MyBrackets.local_time}' WHERE node = '{node}' AND start = end;
    #             INSERT INTO {config.database['report']['table']['status']} (node, status, pool, start, end) VALUES ('{node}', '{mode}', '{pool}', '{MyBrackets.local_time}', '{MyBrackets.local_time}')
    #             '''
    # elif mode == "up":
    #     post_query = f"UPDATE {config.database['report']['table']['status']} SET end = '{MyBrackets.local_time}' WHERE node = '{node}' AND start = end"
    print (f"post_query: {post_query}")
    # logger_win.info (f"post_query: {post_query}") if config.partition['windows']['node'] in node else logger_unix.info (f"post_query: {post_query}")
    logger.info (f"post_query: {post_query}")
    try:
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        if post_query:
            with my_connection.cursor() as my_cursor:
                for query in post_query:
                    my_cursor.execute(query)
                    my_connection.commit()
                # my_cursor.execute(post_query)
                # my_connection.commit()
                    print (f"{my_cursor.rowcount} record(s) inserted into < {config.database['report']['table']['status']} > table") if MyPrintCondition.fprint else 0  
                    # logger_win.info (f"{my_cursor.rowcount} record(s) inserted into < {config.database['report']['table']['status']} > table") if config.partition['windows']['node'] in node else logger_unix.info (f"{my_cursor.rowcount} record(s) inserted into < {config.database['report']['table']['status']} > table")
                    logger.info (f"{my_cursor.rowcount} record(s) inserted into < {config.database['report']['table']['status']} > table")
            if mode != "up":
                refresh (node)
        else:
            print (f"Not possible to apply same mode: < {mode} > to < {node} >") if MyPrintCondition.fprint else 0
            # logger_win.info (f"Not possible to apply same < {mode} > mode to < {node} >") if config.partition['windows']['node'] in node else logger_unix.info (f"Not possible to apply same < {mode} > mode to < {node} >")
            logger.info (f"Not possible to apply same < {mode} > mode to < {node} >")
    except my_connection.Error as e:
        print (f"status record error for node < {node} > in post_query = {post_query}\n{e}") if MyPrintCondition.fprint else 0
        # logger_win.error (f"status record error for node < {node} > in post_query = {post_query}\n{e}") if config.partition['windows']['node'] in node else logger_unix.error (f"status record error for node < {node} > in post_query = {post_query}\n{e}")
        logger.error (f"status record error for node < {node} > in post_query = {post_query}\n{e}")
            
    
    
# def set_status_down(node):
#     pool = ""
#     if config.partition['windows']['node'] in node:
#         pool = "GENERAL" if int(node.removeprefix(config.partition['windows']['node'])) in range(config.partition['windows']['general']['range'][0], config.partition['windows']['general']['range'][1]+1) else "BOOKING"
#     elif config.partition['linux']['node'] in node:
#         pool = "GENERAL" if int(node.removeprefix(config.partition['linux']['node'])) in range(config.partition['linux']['general']['range'][0], config.partition['linux']['general']['range'][1]+1) else "BOOKING"
    
#     query = f"INSERT INTO {config.database['report']['table']['status']} (node, status, pool, start, end) VALUES ('{node}', 'down', '{pool}', '{MyBrackets.local_time}', '{MyBrackets.local_time}')"
#     logger_win.info (f"status_query: {query}") if config.partition['windows']['node'] in node else logger_unix.info (f"status_query: {query}")
#     my_connection.ping()  # reconnecting mysql in case of connection timed out
#     with my_connection.cursor() as my_cursor:
#         my_cursor.execute(query)
#         my_connection.commit()
#     print (f"{my_cursor.rowcount} record(s) inserted into status table") if MyPrintCondition.fprint else 0  
#     logger_win.info (f"{my_cursor.rowcount} record(s) inserted into status table") if config.partition['windows']['node'] in node else logger_unix.info (f"{my_cursor.rowcount} record(s) inserted into status table")

# def set_status_up(node):
#     query = f"UPDATE {config.database['report']['table']['status']} SET status = 'idle', end = {MyBrackets.local_time} WHERE node = '{node}' AND status = 'down', start = end AND start < {MyBrackets.local_time}"
#     logger_win.info (f"status_query: {query}") if config.partition['windows']['node'] in node else logger_unix.info (f"status_query: {query}")
#     my_connection.ping()  # reconnecting mysql in case of connection timed out
#     with my_connection.cursor() as my_cursor:
#         my_cursor.execute(query)
#         my_connection.commit()
#     print (f"{my_cursor.rowcount} record(s) updated in status table") if MyPrintCondition.fprint else 0  
#     logger_win.info (f"{my_cursor.rowcount} record(s) updated in status table") if config.partition['windows']['node'] in node else logger_unix.info (f"{my_cursor.rowcount} record(s) updated in status table")

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