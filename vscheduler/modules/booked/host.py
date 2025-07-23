from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.lib.verbose import verbose
my_connection = MyDatabase.connect_booked_db()

host_records = CaptureLog("host", __file__)
logger = host_records.log_agent("booked")

print("Verbose mode:", verbose.mode)
def host_by_name(hostname):
    """
    Retreives resource id using hostname in booked db
    """
    print("Verbose mode::", verbose.mode)
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
        print (f"\n{tabulate(sentence, headers=['resources_id', 'resources_name'])}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.info (f"\n{tabulate(sentence, headers=['resources_id', 'resources_name'])}")
        return resources_results if resources_results else ""
    except:
        print (f"Resource Error; node < {hostname} > is not a resource in booked\n") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.error (f"Resource Error; node < {hostname} > is not a resource in booked")


def host_by_id(id):
    """
    Retreives resource name (hostname) using resource id in booked db
    """
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
        print (f"\n{tabulate(sentence, headers=['resources_id', 'resources_name'])}") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.info (f"\n{tabulate(sentence, headers=['resources_id', 'resources_name'])}")
        return resources_name
    except:
        print (f"Resource Error; node id < {id} > is not a resource in booked\n") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.error (f"Resource Error; node id < {id} > is not a resource in booked")