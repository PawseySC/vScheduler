# caled by exceptt tool
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.general.timer import Brackets as MyBrackets
import pandas as pd

my_connection = MyDatabase.connect_report_db()

records = Capture_log("exception", __file__)
logger_win = records.log_agent("windows")
logger_unix = records.log_agent("linux")


def activation(node):
    exception_query = f"INSERT INTO {MyCredentials.report_maintenance_table} (node, status, start, end) VALUES '{node}', 'Y', {MyBrackets.local_time}, {MyBrackets.local_time}"
    logger_win.info (f"exception_query: {exception_query}") if MyCredentials.windows_node_name in node else logger_unix.info (f"exception_query: {exception_query}")
    my_connection.ping()  # reconnecting mysql in case of connection timed out
    with my_connection.cursor() as my_cursor:
        my_cursor.execute(exception_query)
        my_connection.commit()
    print (f"{my_cursor.rowcount} record(s) inserted") if MyPrintCondition.fprint else 0  
    logger_win.info (f"{my_cursor.rowcount} record(s) inserted") if MyCredentials.windows_node_name in node else logger_unix.info (f"{my_cursor.rowcount} record(s) inserted")
    # NOTIFY USERS ??? <<<<<<<<
    
def deactivation(node):
    exception_query = f"UPDATE {MyCredentials.report_maintenance_table} SET status = 'N', end = {MyBrackets.local_time} WHERE node = '{node}' AND status = 'DOWN', start = end AND start < {MyBrackets.local_time}"
    logger_win.info (f"exception_query: {exception_query}") if MyCredentials.windows_node_name in node else logger_unix.info (f"exception_query: {exception_query}")
    my_connection.ping()  # reconnecting mysql in case of connection timed out
    with my_connection.cursor() as my_cursor:
        my_cursor.execute(exception_query)
        my_connection.commit()
    print (f"{my_cursor.rowcount} record(s) updated") if MyPrintCondition.fprint else 0  
    logger_win.info (f"{my_cursor.rowcount} record(s) updated") if MyCredentials.windows_node_name in node else logger_unix.info (f"{my_cursor.rowcount} record(s) updated")
    # NOTIFY USERS ??? <<<<<<<<

def activation_status(node, start, end):
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
    actual_status_query = f"SELECT * FROM {MyCredentials.report_maintenance_table}" + query
    actual_status_report_results = pd.read_sql(actual_status_query, my_connection)    