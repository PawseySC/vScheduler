from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.conn_permission import guacamole_connection

my_connection = MyDatabase.connect_guaca_db()

checkpool_records = CaptureLog("checkpool", __file__)
logger = checkpool_records.log_agent("guaca")

def checkpool(node, pool):
    """
    Checks the general pool connection node
    """
    pool_entity = entity(pool)
    connection_id = guacamole_connection(node)
    try:
        sentence = []
        query = f"SELECT connection_id, entity_id FROM guacamole_connection_permission WHERE connection_id = '{connection_id[0][0]}' and entity_id = '{pool_entity[0][0]}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(query)
            query_results = cursor.fetchall()
        if MyPrintCondition.fprint:
            for row_query in query_results:
                connection_id = row_query[0]
                entity_id = row_query[1]
                sentence.insert(len(sentence), [connection_id , entity_id])
        print ("=>EMPTY") if MyPrintCondition.fprint and not query_results else 0 
        logger.info ("=>EMPTY")
        print ("\n", tabulate(sentence, headers=['connection_id', 'entity_id'])) if MyPrintCondition.fprint and query_results else 0
        logger.info ("\n" + tabulate(sentence, headers=['connection_id', 'entity_id']))
        print (f"query_results: {query_results}")
        logger.info (f"query_results: {query_results}")

        return query_results if query_results else ""
    except:
        print (f"error fetching pool info for node < {node} > and pool < {pool} >") if MyPrintCondition.fprint else 0
        logger.error (f"error fetching pool info for node < {node} > and pool < {pool} >")