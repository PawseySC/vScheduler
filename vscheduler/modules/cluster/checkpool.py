# checks the general pool connection node
from tabulate import tabulate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.connperm import guacamole_connection
my_connection = MyDatabase.connect_guaca_db()
my_cursor = my_connection.cursor()

def checkpool(node, pool):
    pool_entity = entity(pool)
    connection_id = guacamole_connection(node)
    try:
        sentence = []
        query = "SELECT connection_id, entity_id FROM guacamole_connection_permission WHERE connection_id = '%s' and entity_id = '%s'" %(connection_id[0][0], pool_entity[0][0])
        my_cursor.execute(query)
        query_results = my_cursor.fetchall()
        if MyPrintCondition.fprint:
            for row_query in query_results:
                connection_id = row_query[0]
                entity_id = row_query[1]
                sentence.insert(len(sentence), [connection_id , entity_id])
        print ("=>EMPTY") if MyPrintCondition.fprint and not query_results else 0 
        print ("\n", tabulate(sentence, headers=['connection_id', 'entity_id'])) if MyPrintCondition.fprint and query_results else 0
        print(query_results)
        return query_results if query_results else ""
    except:
        print (f"error fetching pool info for node <", node, "> and pool <", pool, ">") if MyPrintCondition.fprint else 0