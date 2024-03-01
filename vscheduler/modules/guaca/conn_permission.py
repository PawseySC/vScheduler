# gives the connection to general pool for load balance module
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import PrintCondition as MyPrintCondition

my_connection = MyDatabase.connect_guaca_db()

pool_records = Capture_log("pool", __file__)
logger_win = pool_records.log_agent("windows")
logger_unix = pool_records.log_agent("linux")


def guacamole_connection(node):
    try:
        sentence = []
        connection = f"SELECT connection_id, connection_name FROM guacamole_connection WHERE connection_name = '{node}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(connection)
            connection_results = cursor.fetchall()
        for row_connection in connection_results:
            connection_id = row_connection[0]
            connection_name = row_connection[1]
            sentence.insert(len(sentence), [connection_id , connection_name])
        print ("EMPTY guacamole_connection") if MyPrintCondition.fprint and not connection_results else 0 
        if MyCredentials.windows_node_name in node:
            logger_win.info ("EMPTY guacamole_connection") if not connection_results else 0
        elif MyCredentials.linux_node_name in node:
            logger_unix.info ("EMPTY guacamole_connection") if not connection_results else 0
        print ("\n", tabulate(sentence, headers=['connection_id', 'connection_name'])) if MyPrintCondition.fprint and connection_results else 0
        logger_win.info ("\n" + tabulate(sentence, headers=['connection_id', 'connection_name'])) if MyCredentials.windows_node_name in node else logger_unix.info ("\n" + tabulate(sentence, headers=['connection_id', 'connection_name']))
        return connection_results if connection_results else ""
    except:
        print (f"error fetching connection identification records for < {node} >") if MyPrintCondition.fprint else 0
        logger_win.error (f"error fetching connection identification records for < {node} >") if MyCredentials.windows_node_name in node else logger_unix.error (f"error fetching connection identification records for < {node} >")
    
def connection_permission(conn, pool):
    try:
        conn_name = guacamole_connection(conn)
        check = f"SELECT connection_id, entity_id FROM guacamole_connection_permission WHERE entity_id = '{pool}'"                      # check if pool has any connection
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(check)
            check_results = cursor.fetchall()
        # print ("len(check_results)", len(check_results))
        if len(check_results) == 0:
            assign = f"INSERT INTO guacamole_connection_permission (connection_id, entity_id) VALUES ('{conn_name[0][0]}','{pool}')"      # when no coonection assigned to pool yet
            with my_connection.cursor() as cursor:
                cursor.execute(assign)
                my_connection.commit()
            print (f"{cursor.rowcount} record(s) inserted into guacamole_connection_permission") if MyPrintCondition.fprint else 0 
            logger_win.info (f"{cursor.rowcount} record(s) inserted into guacamole_connection_permission") if MyCredentials.windows_node_name in conn else logger_unix.info (f"{cursor.rowcount} record(s) inserted into guacamole_connection_permission")
        else:
            allocation = f"UPDATE guacamole_connection_permission SET connection_id = '{conn_name[0][0]}' WHERE entity_id = '{pool}'"     # when simeltanous multiple booking allowed
            with my_connection.cursor() as cursor:
                cursor.execute(allocation)
                my_connection.commit()
            print (f"{cursor.rowcount} record(s) affected by updating pool connection permission") if MyPrintCondition.fprint else 0
            logger_win.info (f"{cursor.rowcount} record(s) affected by updating pool connection permission") if MyCredentials.windows_node_name in conn else logger_unix.info (f"{cursor.rowcount} record(s) affected by updating pool connection permission")
    except:
        print (f"error updating the record for entity_id < {conn_name} > and guacamole_connection_permission < {pool} >") if MyPrintCondition.fprint else 0
        logger_win.error (f"error updating the record for entity_id < {conn_name} > and guacamole_connection_permission < {pool} >") if MyCredentials.windows_node_name in conn else logger_unix.error (f"error updating the record for entity_id < {conn_name} > and guacamole_connection_permission < {pool} >")


def del_connection(conn, pool):
    try:
        conn_name = guacamole_connection(conn)
        check = f"SELECT connection_id, entity_id FROM guacamole_connection_permission WHERE entity_id = '{pool}'"                           # check if pool has any connection
        logger_win.info (f"conn_name[0][0]: {conn_name[0][0]}") if MyCredentials.windows_node_name in conn else logger_unix.info (f"conn_name[0][0]: {conn_name[0][0]}")
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(check)
            check_results = cursor.fetchall()
        # print ("len(check_results)", len(check_results))
        if len(check_results) > 0:      # if pool has a connection
            empty = f"DELETE FROM guacamole_connection_permission WHERE connection_id = {conn_name[0][0]} AND entity_id = '{pool}'"
            with my_connection.cursor() as cursor:
                cursor.execute(empty)
                my_connection.commit()
            print (f"{cursor.rowcount} record(s) affected by emptying pool connection permission") if MyPrintCondition.fprint else 0
            logger_win.info (f"{cursor.rowcount} record(s) affected by emptying pool connection permission") if MyCredentials.windows_node_name in conn else logger_unix.info (f"{cursor.rowcount} record(s) affected by emptying pool connection permission")
        else:
            print (f"guacamole general pool < {pool} > has no connection") if MyPrintCondition.fprint else 0
            logger_win.info (f"guacamole general pool < {pool} > has no connection") if MyCredentials.windows_node_name in conn else logger_unix.info (f"guacamole general pool < {pool} > has no connection")
    except:
        print (f"error emptying the pool < {pool} > from connection id/name < {conn_name} >") if MyPrintCondition.fprint else 0
        logger_win.error (f"error emptying the pool < {pool} > from connecion id/name < {conn_name} >") if MyCredentials.windows_node_name in conn else logger_unix.error (f"error emptying the pool < {pool} > from connecion id/name < {conn_name} >")