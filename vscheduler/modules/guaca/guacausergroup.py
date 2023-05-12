# retreives user group in guacamole
from tabulate import tabulate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
connection = MyDatabase.connect_guaca_db()
my_cursor = connection.cursor()


def guacamole_user_group(group_entity):
    try:
        sentence = []
        user_group = "SELECT user_group_id, entity_id FROM guacamole_user_group WHERE entity_id = '%s'" %(group_entity)
        my_cursor.execute(user_group)
        user_group_results = my_cursor.fetchall()
        if MyPrintCondition.fprint:
            for row_user_group in user_group_results:
                user_group_id = row_user_group[0]
                entity_id = row_user_group[1]
                sentence.insert(len(sentence), [user_group_id , entity_id])
        print("\n", tabulate(sentence, headers=['user_group_id', 'entity_id'])) if MyPrintCondition.fprint else 0
        return user_group_results
    except:
        print ("111") if MyPrintCondition.fprint else 0