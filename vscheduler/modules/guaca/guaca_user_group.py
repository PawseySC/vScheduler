# retreives user group in guacamole
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_guaca_db()
my_cursor = my_connection.cursor()

pool_records = Capture_log("pool", __file__)
logger = pool_records.log_agent()

def guacamole_user_group(group_entity):
    try:
        sentence = []
        user_group = f"SELECT user_group_id, entity_id FROM guacamole_user_group WHERE entity_id = {group_entity}"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(user_group)
            user_group_results = cursor.fetchall()
        for row_user_group in user_group_results:
            user_group_id = row_user_group[0]
            entity_id = row_user_group[1]
            sentence.insert(len(sentence), [user_group_id , entity_id])
        print("\n", tabulate(sentence, headers=['user_group_id', 'entity_id'])) if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['user_group_id', 'entity_id']))
        
        my_connection.close()
        return user_group_results
    except:
        print (f"error retreiving user group data for group_entity < {group_entity} >") if MyPrintCondition.fprint else 0
        logger.error (f"error retreiving user group data for group_entity < {group_entity} >")