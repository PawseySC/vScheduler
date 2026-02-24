# retreives series id of each resource in booked
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_booked_db()

booking_records = Capture_log("booking", __file__)
logger_win = booking_records.log_agent("windows")    # **** logger_unix needs to be added; win flag should be sent when calling the function ****


def resource_reservations(resource_id):
    try:
        sentence = []
        reservation_resources = f"SELECT series_id, resource_id FROM reservation_resources WHERE resource_id = '{resource_id}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(reservation_resources)
            reservation_resources_results = cursor.fetchall()
        for row_reservation_resources in reservation_resources_results:
            series_id = row_reservation_resources[0]
            resources_id = row_reservation_resources[1]
            sentence.insert(len(sentence), [resources_id, series_id])
        print ("\n", tabulate(sentence, headers=['resources_id', 'series_id'])) if MyPrintCondition.fprint else 0
        logger_win.info ("\n" + tabulate(sentence, headers=['resources_id', 'series_id']))
        return reservation_resources_results
    except:
        print (f"error: resource with id < {resource_id} > not found") if MyPrintCondition.fprint else 0
        logger_win.error (f"error: resource with id < {resource_id} > not found")