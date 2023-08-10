# retreives quota of user on specific resource in booked
from tabulate import tabulate
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_booked_db()
my_cursor = my_connection.cursor()

booking_records = Capture_log("booking", __file__)
logger = booking_records.log_agent()

def quotas(resources_id, groups_id):
    try:
        sentence = []
        if groups_id and resources_id:
            quota = "SELECT quota_id, quota_limit, unit, duration, resource_id, group_id, schedule_id, enforced_days, enforced_time_start, enforced_time_end FROM quotas WHERE resource_id = '%s' AND group_id = '%s'" %(resources_id, groups_id) 
        elif not groups_id:
            quota = "SELECT quota_id, quota_limit, unit, duration, resource_id, group_id, schedule_id, enforced_days, enforced_time_start, enforced_time_end FROM quotas WHERE resource_id = '%s'" %(resources_id)
        elif not resources_id:
            quota = "SELECT quota_id, quota_limit, unit, duration, resource_id, group_id, schedule_id, enforced_days, enforced_time_start, enforced_time_end FROM quotas WHERE group_id = '%s'" %(groups_id)
            
        my_cursor.execute(quota)
        quota_results = my_cursor.fetchall()
        for row_quota in quota_results:
            quota_id = row_quota[0]
            quota_limit = row_quota[1]
            unit = row_quota[2]
            duration = row_quota[3]
            resource_id = row_quota[4]
            group_id = row_quota[5]
            schedule_id = row_quota[6]
            enforced_days = row_quota[7]
            enforced_time_start = row_quota[8]
            enforced_time_end = row_quota[9]
            sentence.insert(len(sentence), [quota_id , quota_limit, unit, duration, resource_id, group_id, schedule_id, enforced_days, enforced_time_start, enforced_time_end])
        print ("EMPTY quota_results") if MyPrintCondition.fprint and not quota_results else 0
        logger.info ("EMPTY quota_results")
        print ("\n", tabulate(sentence, headers=['quota_id', 'quota_limit', 'unit', 'duration', 'resource_id', 'group_id', 'schedule_id', 'enforced_days', 'enforced_time_start', 'enforced_time_end'])) if MyPrintCondition.fprint and quota_results else 0
        logger.info ("\n" + tabulate(sentence, headers=['quota_id', 'quota_limit', 'unit', 'duration', 'resource_id', 'group_id', 'schedule_id', 'enforced_days', 'enforced_time_start', 'enforced_time_end']))
        return quota_results if quota_results else ""
    except:
        print (f"quota error; resource id < {resources_id} > or group id < {groups_id} > was not found in booked\n") if MyPrintCondition.fprint else 0
        logger.error (f"quota error; resource id < {resources_id} > or group id < {groups_id} > was not found in booked")