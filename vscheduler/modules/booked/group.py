from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.verbose import verbose
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_booked_db()

group_records = CaptureLog("group", __file__)
logger = group_records.log_agent("windbookedows")


def group_id(user_id):
    """
    Retreives user's group id using user id in booked db
    """
    try:
        sentence = []
        group = f"SELECT user_id, group_id FROM user_groups WHERE user_id = '{user_id}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(group)
            group_results = cursor.fetchall()
        for row_group in group_results:
            users_id = row_group[0]
            groups_id = row_group[1]
            sentence.insert(len(sentence), [users_id , groups_id])
        print (f"\n{tabulate(sentence, headers=['users_id', 'groups_id'])}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.info (f"\n{tabulate(sentence, headers=['users_id', 'groups_id'])}")
        return group_results
    except:
        print (f"group error; user id < {user_id} > is not available in booked\n") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.error (f"group error; user id < {user_id} > is not available in booked")


def group_name(group_id):
    """
    Retreives user's group name using group id in booked db
    """
    try:
        sentence = []
        group = f"SELECT group_id, name FROM `groups` WHERE group_id = '{group_id}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(group)
            group_results = cursor.fetchall()
        for row_group in group_results:
            group_id = row_group[0]
            name = row_group[1]
            sentence.insert(len(sentence), [group_id , name])
        print (f"\n{tabulate(sentence, headers=['group_id', 'name'])}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.info (f"\n{tabulate(sentence, headers=['group_id', 'name'])}")
        return group_results
    except:
        print (f"group error; group id < {group_id} > is not available in booked to extract its name\n") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.error (f"group error; group id < {group_id} > is not available in booked to extract its name")


def group_members(group_id):
    """
    Retreives group members using group id in booked db
    """
    try:
        sentence = []
        id = []
        members = f"SELECT user_id, group_id FROM user_groups WHERE group_id = '{group_id}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(members)
            members_results = cursor.fetchall()
        for row_members in members_results:
            users_id = row_members[0]
            groups_id = row_members[1]
            sentence.insert(len(sentence), [users_id , groups_id])
            id.append(users_id)
        print (f"\n{tabulate(sentence, headers=['users_id', 'groups_id'])}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.info (f"\n{tabulate(sentence, headers=['users_id', 'groups_id'])}")
        return id
    except:
        print (f"member error; group id < {group_id} > is not available in booked to extract its members\n") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.error (f"member error; group id < {group_id} > is not available in booked to extract its members")