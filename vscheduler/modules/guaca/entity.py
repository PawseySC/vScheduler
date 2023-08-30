# retreives host and user identy number in guacamole
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_guaca_db()
my_cursor = my_connection.cursor()

pool_records = Capture_log("booking/pool", __file__)
logger = pool_records.log_agent()

def entity(feed):
    try:
        sentence = []
        print (f"entity feed: {feed}") if MyPrintCondition.fprint else 0
        logger.info (f"entity feed: {feed}")
        entity_ids = "SELECT entity_id, name FROM guacamole_entity WHERE name = '%s'" %(feed)
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(entity_ids)
            entity_id_results = cursor.fetchall()
        logger.info (f"entity_id_results, {entity_id_results}")
        for row_entity_id in entity_id_results:
            entity_id = row_entity_id[0]
            name = row_entity_id[1]
            sentence.insert(len(sentence), [entity_id , name])
            logger.info (f"sentence, {sentence}")
        print("\n", tabulate(sentence, headers=['entity_id', 'name'])) if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['entity_id', 'name']))
        
        my_connection.close()
        return  entity_id_results
    except:
        print (f"error: user group record for {feed} was not found in guacamole database") if MyPrintCondition.fprint else 0
        logger.error(f"user group record for {feed} was not found in guacamole database")