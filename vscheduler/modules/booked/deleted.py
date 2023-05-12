# retreives status id of each reservation instances from booked (status id:2 means deleted booking)
from tabulate import tabulate
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_booked_db()
my_cursor = my_connection.cursor()

def deleted(reserved_series):
    try:
        sentence = []
        reservation_series = "SELECT series_id, status_id FROM reservation_series WHERE series_id = '%s'" %(reserved_series)        
        my_cursor.execute(reservation_series)
        reservation_series_results = my_cursor.fetchall()
        if MyPrintCondition.fprint:
            for row_reservation_series in reservation_series_results:
                reservation_series_id = row_reservation_series[0]
                reservation_series_status_id = row_reservation_series[1]
                sentence.insert(len(sentence), [reservation_series_id , reservation_series_status_id])
        print("\n", tabulate(sentence, headers=['reservation_series_id', 'reservation_series_status_id'])) if MyPrintCondition.fprint else 0
        return reservation_series_results
    except:
        print (f"error retreiving resevation series for <", reserved_series, ">") if MyPrintCondition.fprint else 0   


def deleted_records():
    try:
        sentence = []
        reservation_series = "SELECT series_id, status_id FROM reservation_series"      
        my_cursor.execute(reservation_series)
        reservation_series_results = my_cursor.fetchall()
        if MyPrintCondition.fprint:
            for row_reservation_series in reservation_series_results:
                reservation_series_id = row_reservation_series[0]
                reservation_series_status_id = row_reservation_series[1]
                sentence.insert(len(sentence), [reservation_series_id , reservation_series_status_id])
        print("\n", tabulate(sentence, headers=['reservation_series_id', 'reservation_series_status_id'])) if MyPrintCondition.fprint else 0
        return reservation_series_results
    except:
        print ("error retreiving resevation series") if MyPrintCondition.fprint else 0   