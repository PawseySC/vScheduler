# retreives user group in guacamole
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_guaca_db()

pool_records = Capture_log("pool", __file__)
logger_unix = pool_records.log_agent("linux")   # **** logger_win needs to be added; win flag should be sent when calling the function ****

def check_group(user_group):
    try:
        sentence = []
        check_group = f"SELECT user_group_id, member_entity_id FROM guacamole_user_group_member WHERE user_group_id = {user_group}"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(check_group)
            check_group_results = cursor.fetchall()
        if len(check_group_results) == 0:
            print ("EMPTY check_group") if MyPrintCondition.fprint else 0
            logger_unix.info ("EMPTY check_group")
            return
        else:
            for row_check_group in check_group_results:
                user_group_id = row_check_group[0]
                member_entity_id = row_check_group[1]
                sentence.insert(len(sentence), [user_group_id , member_entity_id])
        print ("\n", tabulate(sentence, headers=['user_group_id', 'member_entity_id'])) if MyPrintCondition.fprint else 0
        logger_unix.info ("\n" + tabulate(sentence, headers=['user_group_id', 'member_entity_id']))

        return check_group_results
    except:
        print ("error in checking guacamole user group member") if MyPrintCondition.fprint else 0
        logger_unix.error ("error in checking guacamole user group member")