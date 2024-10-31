# removes/adds users to general pool at maintenance
import guacamole
import pandas as pd
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import PrintCondition as MyPrintCondition

records = Capture_log("maintenance", __file__)
logger_win = records.log_agent("windows")
logger_unix = records.log_agent("linux")

session = guacamole.session("https://dev-guacamole.pawsey.org.au", "mysql", "guacadmin", "pckuW4q4eL9hB2jjZX8R")

def change_maint_status (mode, partition):
    try:
        users = session.list_users()
        general_pool_users = []
        [general_pool_users.append(user) for user in users if partition in session.detail_user_groups(user)]
        general_pool_users_df = pd.DataFrame({'USERNAME':general_pool_users})
        general_pool_users_df[partition] = "*"
        print (f"\n{partition} users: ({len(general_pool_users_df)})\n{general_pool_users_df.sort_values('USERNAME', ascending=True)}") if MyPrintCondition.fprint else 0
        logger_unix.info (f"\n{partition} users: ({len(general_pool_users_df)})\n{general_pool_users_df.sort_values('USERNAME', ascending=True)}") if partition == MyCredentials.linux_pool else 0
        logger_win.info (f"\n{partition} users: ({len(general_pool_users_df)})\n{general_pool_users_df.sort_values('USERNAME', ascending=True)}") if partition == MyCredentials.windows_pool else 0
    except session.error as e:
        print (f"error in checking guacamole users:\n{e}") if MyPrintCondition.fprint else 0
        logger_unix.info (f"error in checking guacamole users:\n{e}") if partition == MyCredentials.linux_pool else 0
        logger_win.info (f"error in checking guacamole users:\n{e}") if partition == MyCredentials.windows_pool else 0
    if mode == "create":
        [(session.update_user_group(user, partition, "remove") for user in general_pool_users_df['USERNAME'].values.tolist())]
        print (f"Maintenance mode successfully enabled for < {partition} >\nusers access to < {partition} > was removed.") if MyPrintCondition.fprint else 0
        logger_unix.info (f"Maintenance mode successfully enabled for < {partition} >\nusers access to < {partition} > was removed.") if partition == MyCredentials.linux_pool else 0
        logger_win.info (f"Maintenance mode successfully enabled for < {partition} >\nusers access to < {partition} > was removed.") if partition == MyCredentials.windows_pool else 0
        # also, need to remove users from allocated nodes
        # ****** change the parttion availability, so vinfo shows that as down <--- For now, manual change in config till design the best solution
    elif mode == "delete":
        [(session.update_user_group(user, partition, "add") for user in general_pool_users_df['USERNAME'].values.tolist())]
        print (f"Maintenance mode successfully disabled for < {partition} >\nusers access to < {partition} > was enabled.") if MyPrintCondition.fprint else 0
        logger_unix (f"Maintenance mode successfully disabled for < {partition} >\nusers access to < {partition} > was enabled.") if partition == MyCredentials.linux_pool else 0
        logger_win (f"Maintenance mode successfully disabled for < {partition} >\nusers access to < {partition} > was enabled.") if partition == MyCredentials.windows_pool else 0
        # no need to put users back to their allocated nodes before maintenance
        # ****** change the parttion availability, so vinfo shows that as up <--- For now, manual change in config till design the best solution   