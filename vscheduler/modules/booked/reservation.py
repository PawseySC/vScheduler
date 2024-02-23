# retreives reservation instance id of bookings in booked for each user
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_booked_db()
my_cursor = my_connection.cursor()

booking_records = Capture_log("booking", __file__)
logger_win = booking_records.log_agent("windows")    # **** logger_unix needs to be added; win flag should be sent when calling the function ****


def user_reservations_by_user_id(id):
    try:
        sentence = []
        reservation_users = f"SELECT reservation_instance_id, user_id FROM reservation_users WHERE user_id = {id}"
        my_cursor.execute(reservation_users)
        reservation_users_results = my_cursor.fetchall()
        for row_reservation_users in reservation_users_results:
            reservation_instance_id = row_reservation_users[0]
            user_id = row_reservation_users[1]
            sentence.insert(len(sentence), [reservation_instance_id , user_id])
        print (f"\n {tabulate(sentence, headers=['reservation_instance_id', 'user_id'])}") if MyPrintCondition.fprint else 0
        logger_win.info (f"\n {tabulate(sentence, headers=['reservation_instance_id', 'user_id'])}")
        return reservation_users_results
    except:
        print (f"error in retreiving reservation for user with user id < {id} >") if MyPrintCondition.fprint else 0
        logger_win.error (f"error in retreiving reservation for user with user id < {id} >")


def user_reservations_by_instance_id(id):
    try:
        sentence = []
        reservation_users = f"SELECT reservation_instance_id, user_id FROM reservation_users WHERE reservation_instance_id = {id}"
        my_cursor.execute(reservation_users)
        reservation_users_results = my_cursor.fetchall()
        for row_reservation_users in reservation_users_results:
            reservation_instance_id = row_reservation_users[0]
            user_id = row_reservation_users[1]
            sentence.insert(len(sentence), [reservation_instance_id , user_id])
        print ("\n", tabulate(sentence, headers=['reservation_instance_id', 'user_id'])) if MyPrintCondition.fprint else 0
        logger_win.info ("\n" + tabulate(sentence, headers=['reservation_instance_id', 'user_id']))
        return reservation_users_results
    except:
        print (f"error in retreiving reservation for user with reservation instance id < {id} >") if MyPrintCondition.fprint else 0
        logger_win.error (f"error in retreiving reservation for user with reservation instance id < {id} >")


def user_reservations():
    try:
        sentence = []
        reservation_users = "SELECT reservation_instance_id, user_id FROM reservation_users"                       
        my_cursor.execute(reservation_users)
        reservation_users_results = my_cursor.fetchall()
        for row_reservation_users in reservation_users_results:
            reservation_instance_id = row_reservation_users[0]
            user_id = row_reservation_users[1]
            sentence.insert(len(sentence), [reservation_instance_id , user_id])
        print ("\n", tabulate(sentence, headers=['reservation_instance_id', 'user_id'])) if MyPrintCondition.fprint else 0
        logger_win.info ("\n" + tabulate(sentence, headers=['reservation_instance_id', 'user_id']))
        return reservation_users_results
    except:
        print ("error in retreiving reservations") if MyPrintCondition.fprint else 0
        logger_win.error ("error in retreiving reservations")