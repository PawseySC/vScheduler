import os, warnings
warnings.filterwarnings('ignore')
import guacamole
import pandas as pd
from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib import config

maintenance_records = CaptureLog("maintenance", __file__)
# logger_win = records.log_agent("windows")
# logger_unix = records.log_agent("linux")
logger = maintenance_records.log_agent("guaca")

session = guacamole.session("https://dev-guacamole.pawsey.org.au", "mysql", "guacadmin", "pckuW4q4eL9hB2jjZX8R")


def change_maint_status (mode, partition):
    """
    Removes/adds users to general pool at maintenance
    """
    # logger_unix.info (f"mode1: {mode}")
    logger.info (f"mode1: {mode}")
    try:
        users = session.list_users()
        general_pool_users = individual_node_users = user_groups = []
        [general_pool_users.append(user) for user in users if partition in session.detail_user_groups(user)]
        general_pool_users_df = pd.DataFrame({'USERNAME':general_pool_users})
        general_pool_users_df[partition] = "*"
        print (f"\n{partition} users: ({len(general_pool_users_df)})\n{general_pool_users_df.sort_values('USERNAME', ascending=True)}") if MyPrintCondition.fprint else 0
        logger.info (f"\n{partition} users: ({len(general_pool_users_df)})\n{general_pool_users_df.sort_values('USERNAME', ascending=True)}") #if partition == config.partition['linux']['general']['pool'] else 0
        # logger_unix.info (f"\n{partition} users: ({len(general_pool_users_df)})\n{general_pool_users_df.sort_values('USERNAME', ascending=True)}") #if partition == config.partition['linux']['general']['pool'] else 0
        # logger_win.info (f"\n{partition} users: ({len(general_pool_users_df)})\n{general_pool_users_df.sort_values('USERNAME', ascending=True)}") #if partition == config.partition['windows']['general']['pool'] else 0
    except session.error as e:
        print (f"error in checking guacamole users:\n{e}") if MyPrintCondition.fprint else 0
        logger.info (f"error in checking guacamole users:\n{e}") if partition == config.partition['linux']['general']['pool'] else 0
        # logger_unix.info (f"error in checking guacamole users:\n{e}") if partition == config.partition['linux']['general']['pool'] else 0
        # logger_win.info (f"error in checking guacamole users:\n{e}") if partition == config.partition['windows']['general']['pool'] else 0
        
    if mode == "create":
        # logger_unix.info (f"mode2: {mode}")
        logger.info (f"mode2: {mode}")
        # [(session.update_user_group(user, partition, "remove"), logger_unix.info (f"< {user} > updated")) for user in general_pool_users_df['USERNAME'].values.tolist()]    # remove users from pool
        [(session.update_user_group(user, partition, "remove"), logger.info (f"< {user} > updated")) for user in general_pool_users_df['USERNAME'].values.tolist()]    # remove users from pool
        # logger_unix.info (f"individual_node_users: {individual_node_users}")
        logger.info (f"individual_node_users: {individual_node_users}")
        for user in users:  # remove users from individual nodes
            user_groups = session.detail_user_groups(user)
            for user_group in user_groups:
                if partition == config.partition['linux']['general']['pool']:
                    # logger_unix.info ("linux pool == partition")
                    logger.info ("linux pool == partition")
                    # logger_unix.info (user_group)
                    logger.info (user_group)
                    if config.partition['linux']['node'] in user_group:
                        # logger_unix.info (user)
                        logger.info (user)
                        individual_node_users.append(user)
                        session.update_user_group(user, user_group, "remove")
                        # logger_unix.info (f"< {user} > updated")
                        logger.info (f"< {user} > updated")
                    # [individual_node_users.append(user) for user in users if config.partition['linux']['node'] in session.detail_user_groups(user)]
                elif partition == config.partition['windows']['general']['pool']:
                    # logger_win.info ("windows pool == partition")
                    logger.info ("windows pool == partition")
                    # logger_win.info (user_group)
                    logger.info (user_group)
                    if config.partition['windows']['node'] in user_group:
                        # logger_win.info (user)
                        logger.info (user)
                        individual_node_users.append(user)
                        session.update_user_group(user, user_group, "remove")
                        # logger_win.info (f"< {user} > updated")
                        logger.info (f"< {user} > updated")
                    # [individual_node_users.append(user) for user in users if config.partition['windows']['node'] in session.detail_user_groups(user)]

        # logger_unix.info (f"individual_node_users: {individual_node_users}")
        logger.info (f"individual_node_users: {individual_node_users}")
        # [(session.update_user_group(user, group, "remove"), logger_unix.info (f"< {user} > updated")) for group in user_groups]
        print (f"Maintenance mode successfully enabled for < {partition} >\nusers access to < {partition} > was removed.") if MyPrintCondition.fprint else 0
        # logger_unix.info (f"Maintenance mode successfully enabled for < {partition} >\nusers access to < {partition} > was removed.") #if partition == config.partition['linux']['general']['pool'] else 0
        logger.info (f"Maintenance mode successfully enabled for < {partition} >\nusers access to < {partition} > was removed.") #if partition == config.partition['linux']['general']['pool'] else 0
        # logger_win.info (f"Maintenance mode successfully enabled for < {partition} >\nusers access to < {partition} > was removed.") #if partition == config.partition['windows']['general']['pool'] else 0
        # also, need to remove users from allocated nodes
        # ****** change the parttion availability, so vinfo shows that as down <--- For now, manual change in config till design the best solution
        
    elif mode == "delete":
        if partition == config.partition['linux']['general']['pool']:
            # ---> query ldap for only setonix_vis users
            try:
                os.system("ldapsearch -H ldaps://ldap-pool.pawsey.org.au -b dc=pawsey,dc=org,dc=au -o ldif-wrap=no -xLLL '(memberof=cn=setonix_vis*)' uid | grep '^uid:' > temp")
                setonix_users = pd.read_csv("temp", header=None, names=["USERNAME"])
                os.system("rm temp")
                setonix_users["USERNAME"] = setonix_users["USERNAME"].str.replace(r"uid: ", "")
                setonix_users["setonix"] = "*"
                print (f"\nSETONIX LDAP: ({len(setonix_users)})\n{setonix_users.sort_values('USERNAME', ascending=True)}") if MyPrintCondition.fprint else 0
                # logger_unix.info (f"\nSETONIX LDAP: ({len(setonix_users)})\n{setonix_users.sort_values('USERNAME', ascending=True)}")
                logger.info (f"\nSETONIX LDAP: ({len(setonix_users)})\n{setonix_users.sort_values('USERNAME', ascending=True)}")
            except os.error as e:
                print (f"error in querying ldap for setonix_vis:\n{e}") if MyPrintCondition.fprint else 0
                # logger_unix.error (f"error in querying ldap for setonix_vis:\n{e}")
                logger.error (f"error in querying ldap for setonix_vis:\n{e}")
            # [(session.update_user_group(user, partition, "add"), logger_unix.info (f"< {user} > updated")) for user in setonix_users['USERNAME'].values.tolist()]
            [(session.update_user_group(user, partition, "add"), logger.info (f"< {user} > updated")) for user in setonix_users['USERNAME'].values.tolist()]
        elif partition == config.partition['windows']['general']['pool']:
            # ---> query ldap for only nebula users
            try:
                os.system("ldapsearch -H ldaps://ldap-pool.pawsey.org.au -b dc=pawsey,dc=org,dc=au -o ldif-wrap=no -xLLL '(memberof=cn=nebula*)' uid | grep '^uid:' > temp")
                nebula_users = pd.read_csv("temp", header=None, names=["USERNAME"])
                os.system("rm temp")
                nebula_users["USERNAME"] = nebula_users["USERNAME"].str.replace(r"uid: ", "")
                nebula_users["nebula"] = "*"
                print (f"\nNEBULA LDAP: ({len(nebula_users)})\n{nebula_users.sort_values('USERNAME', ascending=True)}") if MyPrintCondition.fprint else 0
                # logger_win.info (f"\nNEBULA LDAP: ({len(nebula_users)})\n{nebula_users.sort_values('USERNAME', ascending=True)}")
                logger.info (f"\nNEBULA LDAP: ({len(nebula_users)})\n{nebula_users.sort_values('USERNAME', ascending=True)}")
            except os.error as e:
                print (f"error in querying ldap for nebula:\n{e}") if MyPrintCondition.fprint else 0
                # logger_win.error (f"error in querying ldap for nebula:\n{e}")
                logger.error (f"error in querying ldap for nebula:\n{e}")
            # [(session.update_user_group(user, partition, "add"), logger_unix.info (f"< {user} > updated")) for user in nebula_users['USERNAME'].values.tolist()]
            [(session.update_user_group(user, partition, "add"), logger.info (f"< {user} > updated")) for user in nebula_users['USERNAME'].values.tolist()]

        print (f"Maintenance mode successfully disabled for < {partition} >\nusers access to < {partition} > was enabled.") if MyPrintCondition.fprint else 0
        # logger_unix.info (f"Maintenance mode successfully disabled for < {partition} >\nusers access to < {partition} > was enabled.") #if partition == config.partition['linux']['general']['pool'] else 0
        logger.info (f"Maintenance mode successfully disabled for < {partition} >\nusers access to < {partition} > was enabled.") #if partition == config.partition['linux']['general']['pool'] else 0
        # logger_win.info (f"Maintenance mode successfully disabled for < {partition} >\nusers access to < {partition} > was enabled.") #if partition == config.partition['windows']['general']['pool'] else 0
        # no need to put users back to their allocated nodes before maintenance
        # ****** change the parttion availability, so vinfo shows that as up <--- For now, manual change in config till design the best solution   