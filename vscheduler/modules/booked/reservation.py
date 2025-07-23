from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.verbose import verbose
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_booked_db()

reservation_records = CaptureLog("reservation", __file__)
logger_win = reservation_records.log_agent("booked")


def user_reservations_by_user_id(id):
    """
    Retreives reservation instance id of bookings using user id in booked db 
    """
    try:
        sentence = []
        reservation_users = f"SELECT reservation_instance_id, user_id FROM reservation_users WHERE user_id = '{id}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(reservation_users)
            reservation_users_results = cursor.fetchall()
        for row_reservation_users in reservation_users_results:
            reservation_instance_id = row_reservation_users[0]
            user_id = row_reservation_users[1]
            sentence.insert(len(sentence), [reservation_instance_id , user_id])
        print (f"\n{tabulate(sentence, headers=['reservation_instance_id', 'user_id'])}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger_win.info (f"\n{tabulate(sentence, headers=['reservation_instance_id', 'user_id'])}")
        return reservation_users_results
    except:
        print (f"error in retreiving reservation for user with user id < {id} >") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger_win.error (f"error in retreiving reservation for user with user id < {id} >")


def user_reservations_by_instance_id(id):
    """
    Retreives user id bound to bookings using reservation instance id in booked db 
    """
    try:
        sentence = []
        reservation_users = f"SELECT reservation_instance_id, user_id FROM reservation_users WHERE reservation_instance_id = '{id}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(reservation_users)
            reservation_users_results = cursor.fetchall()
        for row_reservation_users in reservation_users_results:
            reservation_instance_id = row_reservation_users[0]
            user_id = row_reservation_users[1]
            sentence.insert(len(sentence), [reservation_instance_id , user_id])
        print (f"\n{tabulate(sentence, headers=['reservation_instance_id', 'user_id'])}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger_win.info (f"\n{tabulate(sentence, headers=['reservation_instance_id', 'user_id'])}")
        return reservation_users_results
    except:
        print (f"error in retreiving reservation for user with reservation instance id < {id} >") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger_win.error (f"error in retreiving reservation for user with reservation instance id < {id} >")


def user_reservations():
    """
    Retreives reservation instance & user id of bookings in booked db 
    """
    try:
        sentence = []
        reservation_users = "SELECT reservation_instance_id, user_id FROM reservation_users"                       
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(reservation_users)
            reservation_users_results = cursor.fetchall()
        for row_reservation_users in reservation_users_results:
            reservation_instance_id = row_reservation_users[0]
            user_id = row_reservation_users[1]
            sentence.insert(len(sentence), [reservation_instance_id , user_id])
        print (f"\n{tabulate(sentence, headers=['reservation_instance_id', 'user_id'])}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger_win.info (f"\n{tabulate(sentence, headers=['reservation_instance_id', 'user_id'])}")
        return reservation_users_results
    except:
        print ("error in retreiving reservations") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger_win.error ("error in retreiving reservations")