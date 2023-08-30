# gives the connection to general pool for load balance module
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_guaca_db()
my_cursor = my_connection.cursor()

pool_records = Capture_log("pool", __file__)
logger = pool_records.log_agent()

def guacamole_connection(node):
    try:
        sentence = []
        connection = "SELECT connection_id, connection_name FROM guacamole_connection WHERE connection_name = '%s'" %(node)
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor1:
            cursor1.execute(connection)
            connection_results = cursor1.fetchall()
        for row_connection in connection_results:
            connection_id = row_connection[0]
            connection_name = row_connection[1]
            sentence.insert(len(sentence), [connection_id , connection_name])
        print ("EMPTY guacamole_connection") if MyPrintCondition.fprint and not connection_results else 0 
        logger.info ("EMPTY guacamole_connection") if not connection_results else 0
        print ("\n", tabulate(sentence, headers=['connection_id', 'connection_name'])) if MyPrintCondition.fprint and connection_results else 0
        logger.info ("\n" + tabulate(sentence, headers=['connection_id', 'connection_name']))
        return connection_results if connection_results else ""
    except:
        print (f"error fetching connection identification records for < {node} >") if MyPrintCondition.fprint else 0
        logger.error (f"error fetching connection identification records for < {node} >")
    
def connection_permission(conn, pool):
    try:
        conn_name = guacamole_connection(conn)
        check = "SELECT connection_id, entity_id FROM guacamole_connection_permission WHERE entity_id = '%s'" %(pool)                           # check if pool has any connection
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor2:
            cursor2.execute(check)
            check_results = cursor2.fetchall()
        # print ("len(check_results)", len(check_results))
        if len(check_results) == 0:
            assign = "INSERT INTO guacamole_connection_permission (connection_id, entity_id) VALUES ('%s','%s')" %(conn_name[0][0], pool)       # when no coonection assigned to pool yet
            with my_connection.cursor() as cursor5:
                cursor5.execute(assign)
                my_connection.commit()
            print (f"{cursor5.rowcount} record(s) inserted") if MyPrintCondition.fprint else 0 
            logger.info (f"{cursor5.rowcount} record(s) inserted")
        else:
            allocation = "UPDATE guacamole_connection_permission SET connection_id = '%s' WHERE entity_id = '%s'" %(conn_name[0][0], pool)      # when simeltanous multiple booking allowed
            with my_connection.cursor() as cursor6:
                cursor6.execute(allocation)
                my_connection.commit()
            print (f"{cursor6.rowcount} record(s) affected by updating pool connection permission") if MyPrintCondition.fprint else 0
            logger.info (f"{cursor6.rowcount} record(s) affected by updating pool connection permission")
    except:
        print (f"error updating the record for entity_id < {conn_name} > and guacamole_connection_permission < {pool} >") if MyPrintCondition.fprint else 0
        logger.error (f"error updating the record for entity_id < {conn_name} > and guacamole_connection_permission < {pool} >")


def del_connection(conn, pool):
    try:
        conn_name = guacamole_connection(conn)
        check = "SELECT connection_id, entity_id FROM guacamole_connection_permission WHERE entity_id = '%s'" %(pool)                           # check if pool has any connection
        logger.info (f"conn_name[0][0]: {conn_name[0][0]}")
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor3:
            cursor3.execute(check)
            check_results = cursor3.fetchall()
        # print ("len(check_results)", len(check_results))
        if len(check_results) > 0:  # this means if pool has a connection
            empty = "DELETE FROM guacamole_connection_permission WHERE connection_id = '%s' AND entity_id = '%s'" %(conn_name[0][0], pool)
            with my_connection.cursor() as cursor4:
                cursor4.execute(empty)
                my_connection.commit()
            print (f"{cursor4.rowcount} record(s) affected by emptying pool connection permission") if MyPrintCondition.fprint else 0
            logger.info (f"{cursor4.rowcount} record(s) affected by emptying pool connection permission")
        else:
            print (f"guacamole general pool < {pool} > has no connection") if MyPrintCondition.fprint else 0
            logger.info (f"guacamole general pool < {pool} > has no connection")

        # my_connection.close()
        
    except:
        print (f"error emptying the pool < {pool} > from connection id/name < {conn_name} >") if MyPrintCondition.fprint else 0
        logger.error (f"error emptying the pool < {pool} > from connecion id/name < {conn_name} >")