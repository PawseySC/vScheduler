# retreives user identification in booked
from tabulate import tabulate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_booked_db()
my_cursor = my_connection.cursor()


def user_details_print(users_results):
    sentence = []
    users_results_copy = users_results
    if MyPrintCondition.fprint:
        for row_users in users_results:
            user_id = row_users[0]
            fname = row_users[1]
            lname = row_users[2]
            username = row_users[3]
            email = row_users[4]
            sentence.insert(len(sentence), [user_id , fname, lname, username, email])
        print("\n", tabulate(sentence, headers=['user_id', 'fname', 'lname', 'username', 'email']))
    return users_results_copy


def user_details_by_user_id(logged_in_user):
    try:
        sentence = []
        users = "SELECT user_id, fname, lname, username, email FROM users WHERE user_id = '%s'" %(logged_in_user)   
        my_cursor.execute(users)
        users_results = my_cursor.fetchall()
        users_results_copy = user_details_print(users_results)
        return users_results_copy
    except:
        print ("Users Error, no record for current logged in user id <", logged_in_user ,"> in booked") if MyPrintCondition.fprint else 0


def user_details_by_username(logged_in_user):
    try:
        users = "SELECT user_id, fname, lname, username, email FROM users WHERE username = '%s'" %(logged_in_user)   
        my_cursor.execute(users)
        users_results = my_cursor.fetchall()
        users_results_copy = user_details_print(users_results)
        return users_results_copy
    except:
        print ("Users Error, no record for current logged in user <", logged_in_user ,"> in booked") if MyPrintCondition.fprint else 0