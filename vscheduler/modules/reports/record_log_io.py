from datetime import datetime
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.verbose import verbose
from vscheduler.lib.config import Config
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_report_db()

log_io_records = CaptureLog("log_io", __file__)
logger = log_io_records.log_agent("report")
config = Config()


def record_login(user, node, table, pool):
    """
    Records login events in report table
    """
    try:
        start = datetime.now()   
        # logger_win.info (f"table: {table}") if config.get("partition.windows.node") in node else logger_unix.info (f"pool: {pool}")
        # logger_win.info (f"pool: {pool}") if config.get("partition.windows.node") in node else logger_unix.info (f"pool: {pool}")
        # logger_win.info (f"start: {start}") if config.get("partition.windows.node") in node else logger_unix.info (f"start: {start}")
        logger.info (f"table: {table}\npool: {pool}\nstart: {start}")
        query_in = f"INSERT INTO {table} (user, node, pool, start, end) VALUES ('{user}', '{node}', '{pool}', '{start}', '{start}')"
        # logger_win.info (f"login query: {query_in}") if config.get("partition.windows.node") in node else logger_unix.info (f"login query: {query_in}")
        logger.info (f"login query: {query_in}")
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor_in:
            my_cursor_in.execute(query_in)
            my_connection.commit()
        print (f"{my_cursor_in.rowcount} record(s) inserted into < {table} > for < {pool} > partition") if verbose.mode else 0 # if MyPrintCondition.fprint else 0  
        # logger.info (f"{my_cursor_in.rowcount} record(s) inserted into < {table} > for < {pool} > partition") if config.get("partition.windows.node") in node else logger_unix.info (f"{my_cursor_in.rowcount} record(s) inserted into < {table} > for < {pool} > partition")
        logger.info (f"{my_cursor_in.rowcount} record(s) inserted into < {table} > for < {pool} > partition")
        
    except my_connection.Error as e:
        print (f"error inserting records for < {user} >, < {node} > into report database\n{e}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        # logger_win.error(f"error inserting records for < {user} >, < {node} > into report database\n{e}") if config.get("partition.windows.node") in node else logger_unix.error(f"error inserting records for < {user} >, < {node} > into report database\n{e}")
        logger.error(f"error inserting records for < {user} >, < {node} > into report database\n{e}")


def record_logout(user, node, table, pool):
    """
    Records logout events in report table
    """
    try:
        end = datetime.now()
        # logger_win.info (f"table: {table}") if config.get("partition.windows.node") in node else logger_unix.info (f"table: {table}")
        # logger_win.info (f"pool: {pool}") if config.get("partition.windows.node") in node else logger_unix.info (f"pool: {pool}")
        # logger_win.info (f"end: {end}") if config.get("partition.windows.node") in node else logger_unix.info (f"end: {end}")
        logger.info (f"table: {table}\npool: {pool}\nend: {end}")
        query_out = f"UPDATE {table} SET end = '{end}' WHERE user = '{user}' AND node = '{node}' AND pool = '{pool}' AND start = end"
        # logger_win.info (f"logout query: {query_out}") if config.get("partition.windows.node") in node else logger_unix.info (f"logout query: {query_out}")
        logger.info (f"logout query: {query_out}")
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor_out:
            my_cursor_out.execute(query_out)
            my_connection.commit()
        print (f"{my_cursor_out.rowcount} record(s) updated in < {table} > for < {pool} > partition") if verbose.mode else 0 # if MyPrintCondition.fprint else 0  
        logger.info (f"{my_cursor_out.rowcount} record(s) updated in < {table} > for < {pool} > partition") if config.get("partition.windows.node") in node else logger.info (f"{my_cursor_out.rowcount} record(s) updated in < {table} > for < {pool} > partition")
        
    except my_connection.Error as e:
        print (f"error updaing records for {user}, {node} into report database\n{e}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        # logger_win.error(f"error updating records for {user}, {node} into report database\n{e}") if config.get("partition.windows.node") in node else logger_unix.error(f"error updating records for {user}, {node} into report database\n{e}")
        logger.error(f"error updating records for {user}, {node} into report database\n{e}")