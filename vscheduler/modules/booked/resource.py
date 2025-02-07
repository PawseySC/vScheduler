from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_booked_db()

resource_records = CaptureLog("resource", __file__)
logger_win = resource_records.log_agent("booked")


def resource_reservations(resource_id):
    """
    Retreives series id of each resource in booked db
    """
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
        print (f"\n{tabulate(sentence, headers=['resources_id', 'series_id'])}") if MyPrintCondition.fprint else 0
        logger_win.info (f"\n{tabulate(sentence, headers=['resources_id', 'series_id'])}")
        return reservation_resources_results
    except:
        print (f"error: resource with id < {resource_id} > not found") if MyPrintCondition.fprint else 0
        logger_win.error (f"error: resource with id < {resource_id} > not found")