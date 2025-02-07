from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_booked_db()

delete_records = CaptureLog("deleted", __file__)
logger = delete_records.log_agent("booked")


def deleted(reserved_series):
    """
    Finds out if any current matched booking record status in booked db is valid or deleted
    It's done by retreiving status id of each reservation instances from booked db (status id:2 means deleted booking)
    """
    try:
        sentence = []
        reservation_series = f"SELECT series_id, status_id FROM reservation_series WHERE series_id = '{reserved_series}'"  
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(reservation_series)
            reservation_series_results = cursor.fetchall()
        for row_reservation_series in reservation_series_results:
            reservation_series_id = row_reservation_series[0]
            reservation_series_status_id = row_reservation_series[1]
            sentence.insert(len(sentence), [reservation_series_id , reservation_series_status_id])
        print (f"\n{tabulate(sentence, headers=['reservation_series_id', 'reservation_series_status_id'])}") if MyPrintCondition.fprint else 0
        logger.info (f"\n{tabulate(sentence, headers=['reservation_series_id', 'reservation_series_status_id'])}")
        return reservation_series_results
    except:
        print (f"error retreiving resevation series for < {reserved_series} >") if MyPrintCondition.fprint else 0
        logger.error (f"error retreiving resevation series for < {reserved_series} >")


def deleted_records():
    """
    Retreives list of deleted records in booked db
    """
    try:
        sentence = []
        reservation_series = "SELECT series_id, status_id FROM reservation_series"    
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:  
            cursor.execute(reservation_series)
            reservation_series_results = cursor.fetchall()
        for row_reservation_series in reservation_series_results:
            reservation_series_id = row_reservation_series[0]
            reservation_series_status_id = row_reservation_series[1]
            sentence.insert(len(sentence), [reservation_series_id , reservation_series_status_id])
        print (f"\n{tabulate(sentence, headers=['reservation_series_id', 'reservation_series_status_id'])}") if MyPrintCondition.fprint else 0
        logger.info (f"\n{tabulate(sentence, headers=['reservation_series_id', 'reservation_series_status_id'])}")
        return reservation_series_results
    except:
        print ("error retreiving resevation series") if MyPrintCondition.fprint else 0
        logger.error ("error retreiving resevation series")