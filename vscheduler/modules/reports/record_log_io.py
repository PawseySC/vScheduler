import time
from datetime import datetime
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_report_db()

records_io = Capture_log("login/out", __file__)
logger = records_io.log_agent()


def record_login(user, node, table, pool):
    try:
        # table = ""
        # pool = ""
        start = datetime.now() #.strftime('%Y-%m-%d %H:%M:%S')
        # if MyCredentials.linux_node_name in node and int(node.replace(MyCredentials.linux_node_name, "")) in MyCredentials.linux_general_range:
        #     pool = "general"
        #     table = MyCredentials.report_linux_table
        # elif MyCredentials.linux_node_name in node and int(node.replace(MyCredentials.linux_node_name, "")) in MyCredentials.linux_booking_range:
        #     pool = "booking"
        #     table = MyCredentials.report_linux_table        
        # elif MyCredentials.windows_node_name in node and int(node.replace(MyCredentials.windows_node_name, "")) in MyCredentials.windows_general_range:
        #     pool = "general"
        #     table = MyCredentials.report_windows_table
        # elif MyCredentials.windows_node_name in node and int(node.replace(MyCredentials.windows_node_name, "")) in MyCredentials.windows_booking_range:
        #     pool = "booking"
        #     table = MyCredentials.report_windows_table    

        logger.info (f"table: {table}")
        logger.info (f"pool: {pool}")
        logger.info (f"start: {start}")
        # query = "INSERT INTO %s (user, node, pool, start, end) VALUES ('%s', '%s', '%s', '%s', '%s')" %(table, user, node, pool, start, start)
        # query1 = """INSERT INTO %s (user, node, pool, start, end) VALUES (%s, %s, %s, %s, %s);"""
        # tuple1 =  (table, user, node, pool, start, start)
        query_in = f"INSERT INTO {table} (user, node, pool, start, end) VALUES ('{user}', '{node}', '{pool}', '{start}', '{start}')"
        logger.info (f"login query: {query_in}")
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor_in:
            my_cursor_in.execute(query_in)
            my_connection.commit()
        print (f"{my_cursor_in.rowcount} record(s) inserted") if MyPrintCondition.fprint else 0  
        logger.info (f"{my_cursor_in.rowcount} record(s) inserted")
        
    except my_connection.Error as e:
        print (f"error inserting records for {user}, {node} into report database\n{e}") if MyPrintCondition.fprint else 0
        logger.error(f"error inserting records for {user}, {node} into report database\n{e}")


def record_logout(user, node, table, pool):
    try:
        # table = ""
        # pool = ""
        end = datetime.now() #.strftime('%Y-%m-%d %H:%M:%S')
        # if MyCredentials.linux_node_name in node and int(node.replace(MyCredentials.linux_node_name, "")) in MyCredentials.linux_general_range:
        #     pool = "general"
        #     table = MyCredentials.report_linux_table
        # elif MyCredentials.linux_node_name in node and int(node.replace(MyCredentials.linux_node_name, "")) in MyCredentials.linux_booking_range:
        #     pool = "booking"
        #     table = MyCredentials.report_linux_table        
        # elif MyCredentials.windows_node_name in node and int(node.replace(MyCredentials.windows_node_name, "")) in MyCredentials.windows_general_range:
        #     pool = "general"
        #     table = MyCredentials.report_windows_table
        # elif MyCredentials.windows_node_name in node and int(node.replace(MyCredentials.windows_node_name, "")) in MyCredentials.windows_booking_range:
        #     pool = "booking"
        #     table = MyCredentials.report_windows_table    

        logger.info (f"table: {table}")
        logger.info (f"pool: {pool}")
        logger.info (f"end: {end}")
        # query = "UPDATE %s SET end = '%s' WHERE user = '%s' AND node = '%s' AND pool = '%s' AND start = end" %(table, end, user, node, pool)
        # query2 = "UPDATE %s SET end = %s WHERE user = %s AND node = %s AND pool = %s AND start = end"
        # tuple2 =  (table, end, user, node, pool)
        query_out = f"UPDATE {table} SET end = '{end}' WHERE user = '{user}' AND node = '{node}' AND pool = '{pool}' AND start = end"
        logger.info (f"logout query: {query_out}")
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor_out:
            my_cursor_out.execute(query_out)
            my_connection.commit()
        print (f"{my_cursor_out.rowcount} record(s) updated") if MyPrintCondition.fprint else 0  
        logger.info (f"{my_cursor_out.rowcount} record(s) updated")
        
    except my_connection.Error as e:
        print (f"error updaing records for {user}, {node} into report database\{e}") if MyPrintCondition.fprint else 0
        logger.error(f"error updating records for {user}, {node} into report database\n{e}")