from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_booked_db()

user_records = CaptureLog("user", __file__)
logger_win = user_records.log_agent("booked")


def user_details_print(users_results):
    """
    Prints query results and returns copy of results
    The reason is by printing tupple, cursor sits at the end and returns empty tupple >>> **This could be optimised** <<<
    """
    sentence = []
    users_results_copy = users_results
    for row_users in users_results:
        user_id = row_users[0]
        fname = row_users[1]
        lname = row_users[2]
        username = row_users[3]
        email = row_users[4]
        sentence.insert(len(sentence), [user_id , fname, lname, username, email])
    print (f"\n{tabulate(sentence, headers=['user_id', 'fname', 'lname', 'username', 'email'])}") if MyPrintCondition.fprint else 0
    logger_win.info (f"\n{tabulate(sentence, headers=['user_id', 'fname', 'lname', 'username', 'email'])}")
    return users_results_copy


"""
All below functions return user(s) identifications using user id or username
"""
def user_details_by_user_id(logged_in_user):
    try:
        users = f"SELECT user_id, fname, lname, username, email FROM users WHERE user_id = '{logged_in_user}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(users)
            users_results = cursor.fetchall()
        users_results_copy = user_details_print(users_results)
        return users_results_copy
    except:
        print (f"Users Error, no record for current logged in user id < {logged_in_user} > in booked") if MyPrintCondition.fprint else 0
        logger_win.error (f"Users Error, no record for current logged in user id < {logged_in_user} > in booked")


def user_details_by_username(logged_in_user):
    try:
        users = f"SELECT user_id, fname, lname, username, email FROM users WHERE username = '{logged_in_user}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(users)
            users_results = cursor.fetchall()
        users_results_copy = user_details_print(users_results)
        return users_results_copy
    except:
        print (f"Users Error, no record for current logged in user < {logged_in_user} > in booked") if MyPrintCondition.fprint else 0
        logger_win.error (f"Users Error, no record for current logged in user < {logged_in_user} > in booked")


def user_details():
    try:
        users = "SELECT user_id, fname, lname, username, email FROM users"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(users)
            users_results = cursor.fetchall()
        users_results_copy = user_details_print(users_results)
        return users_results_copy
    except:
        print ("Users Error, no record for users in booked") if MyPrintCondition.fprint else 0
        logger_win.error ("Users Error, no record for users in booked")