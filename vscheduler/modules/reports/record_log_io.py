# records login/out events in relevant report table
from datetime import datetime
from vscheduler.log.log import Capture_log
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import PrintCondition as MyPrintCondition

my_connection = MyDatabase.connect_report_db()

records_io = Capture_log("login/out", __file__)
logger_win = records_io.log_agent("windows")
logger_unix = records_io.log_agent("linux")


def record_login(user, node, table, pool):
    try:
        start = datetime.now()   
        logger_win.info (f"table: {table}") if MyCredentials.windows_node_name in node else logger_unix.info (f"pool: {pool}")
        logger_win.info (f"pool: {pool}") if MyCredentials.windows_node_name in node else logger_unix.info (f"pool: {pool}")
        logger_win.info (f"start: {start}") if MyCredentials.windows_node_name in node else logger_unix.info (f"start: {start}")
        query_in = f"INSERT INTO {table} (user, node, pool, start, end) VALUES ('{user}', '{node}', '{pool}', '{start}', '{start}')"
        logger_win.info (f"login query: {query_in}") if MyCredentials.windows_node_name in node else logger_unix.info (f"login query: {query_in}")
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor_in:
            my_cursor_in.execute(query_in)
            my_connection.commit()
        print (f"{my_cursor_in.rowcount} record(s) inserted into < {table} > for < {pool} > partition") if MyPrintCondition.fprint else 0  
        logger_win.info (f"{my_cursor_in.rowcount} record(s) inserted into < {table} > for < {pool} > partition") if MyCredentials.windows_node_name in node else logger_unix.info (f"{my_cursor_in.rowcount} record(s) inserted into < {table} > for < {pool} > partition")
        
    except my_connection.Error as e:
        print (f"error inserting records for < {user} >, < {node} > into report database\n{e}") if MyPrintCondition.fprint else 0
        logger_win.error(f"error inserting records for < {user} >, < {node} > into report database\n{e}") if MyCredentials.windows_node_name in node else logger_unix.error(f"error inserting records for < {user} >, < {node} > into report database\n{e}")


def record_logout(user, node, table, pool):
    try:
        end = datetime.now()
        logger_win.info (f"table: {table}") if MyCredentials.windows_node_name in node else logger_unix.info (f"table: {table}")
        logger_win.info (f"pool: {pool}") if MyCredentials.windows_node_name in node else logger_unix.info (f"pool: {pool}")
        logger_win.info (f"end: {end}") if MyCredentials.windows_node_name in node else logger_unix.info (f"end: {end}")
        query_out = f"UPDATE {table} SET end = '{end}' WHERE user = '{user}' AND node = '{node}' AND pool = '{pool}' AND start = end"
        logger_win.info (f"logout query: {query_out}") if MyCredentials.windows_node_name in node else logger_unix.info (f"logout query: {query_out}")
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor_out:
            my_cursor_out.execute(query_out)
            my_connection.commit()
        print (f"{my_cursor_out.rowcount} record(s) updated in < {table} > for < {pool} > partition") if MyPrintCondition.fprint else 0  
        logger_win.info (f"{my_cursor_out.rowcount} record(s) updated in < {table} > for < {pool} > partition") if MyCredentials.windows_node_name in node else logger_unix.info (f"{my_cursor_out.rowcount} record(s) updated in < {table} > for < {pool} > partition")
        
    except my_connection.Error as e:
        print (f"error updaing records for {user}, {node} into report database\n{e}") if MyPrintCondition.fprint else 0
        logger_win.error(f"error updating records for {user}, {node} into report database\n{e}") if MyCredentials.windows_node_name in node else logger_unix.error(f"error updating records for {user}, {node} into report database\n{e}")