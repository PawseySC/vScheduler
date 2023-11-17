# retreives reservation instance id, series id, and timeline of bookings from booked for determined time bracket in config
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_booked_db()
my_cursor = my_connection.cursor()

booking_records = Capture_log("booking", __file__)
logger = booking_records.log_agent()

def reservation_instances(start_bracket, end_bracket):
    try:
        sentence = []
        reservation_instances = "SELECT reservation_instance_id, start_date, end_date, series_id FROM reservation_instances WHERE end_date <= '%s' AND start_date >= '%s'" %(end_bracket, start_bracket)
        my_cursor.execute(reservation_instances)
        reservation_instances_results = my_cursor.fetchall()
        for row_reservation_instances in reservation_instances_results:
            reservation_instance_id = row_reservation_instances[0]
            start_date = row_reservation_instances[1]
            end_date = row_reservation_instances[2]
            series_id = row_reservation_instances[3]
            sentence.insert(len(sentence), [reservation_instance_id , start_date, end_date, series_id])
        print ("\n", tabulate(sentence, headers=['reservation_instance_id', 'start_date', 'end_date', 'series_id'])) if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['reservation_instance_id', 'start_date', 'end_date', 'series_id']))
        return reservation_instances_results
    except:
        print ("error retreiving reservation instances") if MyPrintCondition.fprint else 0
        logger.error ("error retreiving reservation instances")