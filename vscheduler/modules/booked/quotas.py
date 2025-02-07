from tabulate import tabulate
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_booked_db()

quotas_records = CaptureLog("quotas", __file__)
logger_win = quotas_records.log_agent("booked")


def quotas(resources_id, groups_id):
    """
    Retreives user quota in booked db for specific resource
    """
    try:
        sentence = []
        if groups_id and resources_id:
            quota = f"SELECT quota_id, quota_limit, unit, duration, resource_id, group_id, schedule_id, enforced_days, enforced_time_start, enforced_time_end FROM quotas WHERE resource_id = '{resources_id}' AND group_id = '{groups_id}'"
        elif not groups_id:
            quota = f"SELECT quota_id, quota_limit, unit, duration, resource_id, group_id, schedule_id, enforced_days, enforced_time_start, enforced_time_end FROM quotas WHERE resource_id = '{resources_id}'"
        elif not resources_id:
            quota = f"SELECT quota_id, quota_limit, unit, duration, resource_id, group_id, schedule_id, enforced_days, enforced_time_start, enforced_time_end FROM quotas WHERE group_id = '{groups_id}'"
            
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor: 
            cursor.execute(quota)
            quota_results = cursor.fetchall()
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
        logger_win.info ("EMPTY quota_results")
        print (f"\n{tabulate(sentence, headers=['quota_id', 'quota_limit', 'unit', 'duration', 'resource_id', 'group_id', 'schedule_id', 'enforced_days', 'enforced_time_start', 'enforced_time_end'])}") if MyPrintCondition.fprint and quota_results else 0
        logger_win.info (f"\n{tabulate(sentence, headers=['quota_id', 'quota_limit', 'unit', 'duration', 'resource_id', 'group_id', 'schedule_id', 'enforced_days', 'enforced_time_start', 'enforced_time_end'])}")
        return quota_results if quota_results else ""
    except:
        print (f"quota error; resource id < {resources_id} > or group id < {groups_id} > was not found in booked\n") if MyPrintCondition.fprint else 0
        logger_win.error (f"quota error; resource id < {resources_id} > or group id < {groups_id} > was not found in booked")