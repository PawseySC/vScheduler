from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_booked_db()

instances_records = CaptureLog("instances", __file__)
logger = instances_records.log_agent("booked")


def reservation_instances(start_bracket, end_bracket):
    """
    Retreives reservation instance id, series id, and bookings timeline from booked db filtered by time bracket in config
    """
    try:
        sentence = []
        reservation_instances = f"SELECT reservation_instance_id, start_date, end_date, series_id FROM reservation_instances WHERE end_date <= '{end_bracket}' AND start_date >= '{start_bracket}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(reservation_instances)
            reservation_instances_results = cursor.fetchall()
        for row_reservation_instances in reservation_instances_results:
            reservation_instance_id = row_reservation_instances[0]
            start_date = row_reservation_instances[1]
            end_date = row_reservation_instances[2]
            series_id = row_reservation_instances[3]
            sentence.insert(len(sentence), [reservation_instance_id , start_date, end_date, series_id])
        print (f"\n{tabulate(sentence, headers=['reservation_instance_id', 'start_date', 'end_date', 'series_id'])}") if MyPrintCondition.fprint else 0
        logger.info (f"\n{tabulate(sentence, headers=['reservation_instance_id', 'start_date', 'end_date', 'series_id'])}")
        return reservation_instances_results
    except:
        print ("error retreiving reservation instances") if MyPrintCondition.fprint else 0
        logger.error ("error retreiving reservation instances")