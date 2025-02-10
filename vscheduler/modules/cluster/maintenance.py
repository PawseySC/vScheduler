from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib import config
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.general.timer import Brackets as MyBrackets
import pandas as pd

my_connection = MyDatabase.connect_report_db()

maintenance_records = CaptureLog("maintenance", __file__)
logger = maintenance_records.log_agent("cluster")


def activation(node):
    """
    Is called by except tool to activate/flag the node as maint in the db 
    """
    # exception_query = f"INSERT INTO {MyCredentials.report_maintenance_table} (node, status, start, end) VALUES '{node}', 'Y', {MyBrackets.local_time}, {MyBrackets.local_time}"
    exception_query = f"INSERT INTO {config.database['report']['status']} (node, status, start, end) VALUES '{node}', 'Y', {MyBrackets.local_time}, {MyBrackets.local_time}"
    # logger_win.info (f"exception_query: {exception_query}") if config.partition['windows']['node'] in node else logger_unix.info (f"exception_query: {exception_query}")
    logger.info (f"exception_query: {exception_query}")
    my_connection.ping()  # reconnecting mysql in case of connection timed out
    with my_connection.cursor() as my_cursor:
        my_cursor.execute(exception_query)
        my_connection.commit()
    print (f"{my_cursor.rowcount} record(s) inserted") if MyPrintCondition.fprint else 0  
    # logger_win.info (f"{my_cursor.rowcount} record(s) inserted") if config.partition['windows']['node'] in node else logger_unix.info (f"{my_cursor.rowcount} record(s) inserted")
    logger.info (f"{my_cursor.rowcount} record(s) inserted")
    # NOTIFY USERS ??? <<<<<<<<
    
def deactivation(node):
    """
    Is called by except tool to deactivate/deflag the node as maint in the db 
    """
    exception_query = f"UPDATE {config.database['report']['status']} SET status = 'N', end = {MyBrackets.local_time} WHERE node = '{node}' AND status = 'DOWN', start = end AND start < {MyBrackets.local_time}"
    # logger_win.info (f"exception_query: {exception_query}") if config.partition['windows']['node'] in node else logger_unix.info (f"exception_query: {exception_query}")
    logger.info (f"exception_query: {exception_query}")
    my_connection.ping()  # reconnecting mysql in case of connection timed out
    with my_connection.cursor() as my_cursor:
        my_cursor.execute(exception_query)
        my_connection.commit()
    print (f"{my_cursor.rowcount} record(s) updated") if MyPrintCondition.fprint else 0  
    # logger_win.info (f"{my_cursor.rowcount} record(s) updated") if config.partition['windows']['node'] in node else logger_unix.info (f"{my_cursor.rowcount} record(s) updated")
    logger.info (f"{my_cursor.rowcount} record(s) updated")
    # NOTIFY USERS ??? <<<<<<<<

def activation_status(node, start, end):
    """
    Is called by except tool to get node status in the db 
    """
    query = " WHERE " if node or start or end else 0
    if query:
        if node:
            query = query + f"node = '{node}'"
            if start:
                query = query + f" AND start = '{start}'"
                if end:
                    query = query + f" AND end = '{end}"
        else:
            if start:
                query = query + f" AND start = '{start}'"
                if end:
                    query = query + f" AND end = '{end}"
            else:
                if end:
                    query = query + f" AND end = '{end}"

    print (query)
    actual_status_query = f"SELECT * FROM {config.database['report']['status']}" + query
    actual_status_report_results = pd.read_sql(actual_status_query, my_connection)    