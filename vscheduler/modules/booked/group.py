# retreives users group id and name in booked
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_booked_db()
my_cursor = my_connection.cursor()

booking_records = Capture_log("booking", __file__)
logger = booking_records.log_agent()

def group_id(user_id):
    try:
        sentence = []
        group = "SELECT user_id, group_id FROM user_groups WHERE user_id = '%s'" %(user_id)
        my_cursor.execute(group)
        group_results = my_cursor.fetchall()
        for row_group in group_results:
            users_id = row_group[0]
            groups_id = row_group[1]
            sentence.insert(len(sentence), [users_id , groups_id])
        print ("\n", tabulate(sentence, headers=['users_id', 'groups_id'])) if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['users_id', 'groups_id']))
        return group_results
    except:
        print (f"group error; user id < {user_id} > is not available in booked\n") if MyPrintCondition.fprint else 0
        logger.error (f"group error; user id < {user_id} > is not available in booked\n")


def group_name(group_id):
    try:
        sentence = []
        group = "SELECT group_id, name FROM `groups` WHERE group_id = '%s'" %(group_id)
        my_cursor.execute(group)
        group_results = my_cursor.fetchall()
        for row_group in group_results:
            group_id = row_group[0]
            name = row_group[1]
            sentence.insert(len(sentence), [group_id , name])
        print ("\n", tabulate(sentence, headers=['group_id', 'name'])) if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['group_id', 'name']))
        return group_results
    except:
        print (f"group error; group id < {group_id} > is not available in booked to extract its name\n") if MyPrintCondition.fprint else 0
        logger.error (f"group error; group id < {group_id} > is not available in booked to extract its name\n")


def group_members(group_id):
    try:
        sentence = []
        id = []
        members = "SELECT user_id, group_id FROM user_groups WHERE group_id = '%s'" %(group_id)
        my_cursor.execute(members)
        members_results = my_cursor.fetchall()
        for row_members in members_results:
            users_id = row_members[0]
            groups_id = row_members[1]
            sentence.insert(len(sentence), [users_id , groups_id])
            id.append(users_id)
        print ("\n", tabulate(sentence, headers=['users_id', 'groups_id'])) if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['users_id', 'groups_id']))
        return id
    except:
        print (f"member error; group id < {group_id} > is not available in booked to extract its members\n") if MyPrintCondition.fprint else 0
        logger.error (f"member error; group id < {group_id} > is not available in booked to extract its members\n")