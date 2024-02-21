# retreives status id of each reservation instances from booked (status id:2 means deleted booking)
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_booked_db()
my_cursor = my_connection.cursor()

booking_records = Capture_log("booking", __file__)
logger = booking_records.log_agent()


def deleted(reserved_series):
    try:
        sentence = []
        reservation_series = f"SELECT series_id, status_id FROM reservation_series WHERE series_id = {reserved_series}"  
        my_cursor.execute(reservation_series)
        reservation_series_results = my_cursor.fetchall()
        for row_reservation_series in reservation_series_results:
            reservation_series_id = row_reservation_series[0]
            reservation_series_status_id = row_reservation_series[1]
            sentence.insert(len(sentence), [reservation_series_id , reservation_series_status_id])
        print ("\n", tabulate(sentence, headers=['reservation_series_id', 'reservation_series_status_id'])) if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['reservation_series_id', 'reservation_series_status_id']))
        return reservation_series_results
    except:
        print (f"error retreiving resevation series for < {reserved_series} >") if MyPrintCondition.fprint else 0
        logger.error (f"error retreiving resevation series for < {reserved_series} >")


def deleted_records():
    try:
        sentence = []
        reservation_series = "SELECT series_id, status_id FROM reservation_series"      
        my_cursor.execute(reservation_series)
        reservation_series_results = my_cursor.fetchall()
        for row_reservation_series in reservation_series_results:
            reservation_series_id = row_reservation_series[0]
            reservation_series_status_id = row_reservation_series[1]
            sentence.insert(len(sentence), [reservation_series_id , reservation_series_status_id])
        print ("\n", tabulate(sentence, headers=['reservation_series_id', 'reservation_series_status_id'])) if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['reservation_series_id', 'reservation_series_status_id']))
        return reservation_series_results
    except:
        print ("error retreiving resevation series") if MyPrintCondition.fprint else 0
        logger.error ("error retreiving resevation series")