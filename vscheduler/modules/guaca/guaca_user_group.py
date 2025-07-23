from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.verbose import verbose
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_guaca_db()

guaca_usergroup_records = CaptureLog("guaca_usergroup", __file__)
logger = guaca_usergroup_records.log_agent("guaca")


def guacamole_user_group(group_entity):
    """
    Retreives user group in guacamole
    """
    try:
        sentence = []
        user_group = f"SELECT user_group_id, entity_id FROM guacamole_user_group WHERE entity_id = '{group_entity}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(user_group)
            user_group_results = cursor.fetchall()
        for row_user_group in user_group_results:
            user_group_id = row_user_group[0]
            entity_id = row_user_group[1]
            sentence.insert(len(sentence), [user_group_id , entity_id])
        print("\n", tabulate(sentence, headers=['user_group_id', 'entity_id'])) if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['user_group_id', 'entity_id']))

        return user_group_results
    except:
        print (f"error retreiving user group data for group_entity < {group_entity} >") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.error (f"error retreiving user group data for group_entity < {group_entity} >")