# retreives host identification in booked
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_booked_db()

booking_records = Capture_log("booking", __file__)
logger_win = booking_records.log_agent("windows")    # **** logger_unix needs to be added; win flag should be sent when calling the function ****


def host_by_name(hostname):
    try:
        sentence = []
        resources = f"SELECT resource_id, name FROM resources WHERE name = '{hostname}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(resources)
            resources_results = cursor.fetchall()
        for row_resources in resources_results:
            resources_id = row_resources[0]
            resources_name = row_resources[1]
            sentence.insert(len(sentence), [resources_id , resources_name])
        print ("\n", tabulate(sentence, headers=['resources_id', 'resources_name'])) if MyPrintCondition.fprint else 0
        logger_win.info ("\n" + tabulate(sentence, headers=['resources_id', 'resources_name']))
        return resources_results if resources_results else ""
    except:
        print (f"Resource Error; node < {hostname} > is not a resource in booked\n") if MyPrintCondition.fprint else 0
        logger_win.error (f"Resource Error; node < {hostname} > is not a resource in booked")


def host_by_id(id):
    try:
        sentence = []
        resources = f"SELECT resource_id, name FROM resources WHERE resource_id = '{id}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(resources)
            resources_results = cursor.fetchall()
        for row_resources in resources_results:
            resources_id = row_resources[0]
            resources_name = row_resources[1]
            sentence.insert(len(sentence), [resources_id , resources_name])
        print ("\n", tabulate(sentence, headers=['resources_id', 'resources_name'])) if MyPrintCondition.fprint else 0
        logger_win.info ("\n" + tabulate(sentence, headers=['resources_id', 'resources_name']))
        return resources_name
    except:
        print (f"Resource Error; node id < {id} > is not a resource in booked\n") if MyPrintCondition.fprint else 0
        logger_win.error (f"Resource Error; node id < {id} > is not a resource in booked")