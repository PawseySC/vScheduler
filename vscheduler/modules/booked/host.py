# retreives host identification in booked
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_booked_db()
my_cursor = my_connection.cursor()

booking_records = Capture_log("booking", __file__)
logger = booking_records.log_agent()

def host_by_name(hostname):
    try:
        sentence = []
        resources = "SELECT resource_id, name FROM resources WHERE name = '%s'" %(hostname)
        my_cursor.execute(resources)
        resources_results = my_cursor.fetchall()
        for row_resources in resources_results:
            resources_id = row_resources[0]
            resources_name = row_resources[1]
            sentence.insert(len(sentence), [resources_id , resources_name])
        print ("\n", tabulate(sentence, headers=['resources_id', 'resources_name'])) if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['resources_id', 'resources_name']))
        return resources_results if resources_results else ""
    except:
        print (f"Resource Error; node < {hostname} > is not a resource in booked\n") if MyPrintCondition.fprint else 0
        logger.error (f"Resource Error; node < {hostname} > is not a resource in booked")


def host_by_id(id):
    try:
        sentence = []
        resources = "SELECT resource_id, name FROM resources WHERE resource_id = '%s'" %(id)
        my_cursor.execute(resources)
        resources_results = my_cursor.fetchall()
        for row_resources in resources_results:
            resources_id = row_resources[0]
            resources_name = row_resources[1]
            sentence.insert(len(sentence), [resources_id , resources_name])
        print ("\n", tabulate(sentence, headers=['resources_id', 'resources_name'])) if MyPrintCondition.fprint else 0
        logger.info ("\n" + tabulate(sentence, headers=['resources_id', 'resources_name']))
        return resources_name
    except:
        print (f"Resource Error; node id < {id} > is not a resource in booked\n") if MyPrintCondition.fprint else 0
        logger.error (f"Resource Error; node id < {id} > is not a resource in booked")