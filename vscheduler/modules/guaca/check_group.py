from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.verbose import verbose
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_guaca_db()

checkgroup_records = CaptureLog("checkgroup", __file__)
logger = checkgroup_records.log_agent("guaca")

def check_group(user_group):
    """
    Retreives user group in guacamole
    """
    try:
        sentence = []
        check_group = f"SELECT user_group_id, member_entity_id FROM guacamole_user_group_member WHERE user_group_id = '{user_group}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(check_group)
            check_group_results = cursor.fetchall()
        if len(check_group_results) == 0:
            print ("EMPTY check_group") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
            logger.info ("EMPTY check_group")
            return
        else:
            for row_check_group in check_group_results:
                user_group_id = row_check_group[0]
                member_entity_id = row_check_group[1]
                sentence.insert(len(sentence), [user_group_id , member_entity_id])
        print ("\n", tabulate(sentence, headers=['user_group_id', 'member_entity_id'])) if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['user_group_id', 'member_entity_id']))

        return check_group_results
    except:
        print ("error in checking guacamole user group member") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.error ("error in checking guacamole user group member")