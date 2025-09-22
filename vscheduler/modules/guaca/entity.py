from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.verbose import verbose
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_guaca_db()

entity_records = CaptureLog("entity", __file__)
logger = entity_records.log_agent("guaca")


def entity(feed):   # os should be sent over for logging into 1 file only
    """
    Retreives host and user identy number in guacamole db
    """
    try:
        sentence = []
        print (f"entity feed: {feed}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.info (f"entity feed: {feed}")
        entity_ids = f"SELECT entity_id, name FROM guacamole_entity WHERE name = '{feed}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(entity_ids)
            entity_id_results = cursor.fetchall()
        logger.info (f"entity_id_results: {entity_id_results}")
        for row_entity_id in entity_id_results:
            entity_id = row_entity_id[0]
            name = row_entity_id[1]
            sentence.insert(len(sentence), [entity_id , name])
            logger.info (f"sentence: {sentence}")
        if not entity_id_results:
            logger.error(f"No entity found for < {feed} >")
            raise Exception("No entity found")
        print("\n", tabulate(sentence, headers=['entity_id', 'name'])) if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['entity_id', 'name']))
        
        return  entity_id_results
    except:
        print (f"error: user group record for < {feed} > was not found in guacamole database") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.error(f"user group record for < {feed} > was not found in guacamole database")