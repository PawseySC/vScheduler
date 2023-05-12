# retreives user group in guacamole
from tabulate import tabulate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_guaca_db()
my_cursor = my_connection.cursor()


def check_group(user_group):
    try:
        sentence = []
        check_group = "SELECT user_group_id, member_entity_id FROM guacamole_user_group_member WHERE user_group_id = '%s'" %(user_group)
        my_cursor.execute(check_group)
        check_group_results = my_cursor.fetchall()
        if len(check_group_results) == 0:
            print ("EMPTY") if MyPrintCondition.fprint else 0
            return
        else:
            if MyPrintCondition.fprint:
                for row_check_group in check_group_results:
                    user_group_id = row_check_group[0]
                    member_entity_id = row_check_group[1]
                    sentence.insert(len(sentence), [user_group_id , member_entity_id])
        print("\n", tabulate(sentence, headers=['user_group_id', 'member_entity_id'])) if MyPrintCondition.fprint else 0
        return check_group_results
    except:
        print ("error in checking guacamole user group member") if MyPrintCondition.fprint else 0