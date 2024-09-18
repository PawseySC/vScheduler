# called by stat tool
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.general.timer import Brackets as MyBrackets

my_connection = MyDatabase.connect_report_db()

records = Capture_log("admin", __file__)
logger_admin = records.log_agent("admin")


def admin_list(user):
    """
    Lists admins list or queries admin status for specific user.
    """
    try:
        admin_list_query = f"SELECT user, start, end FROM {MyCredentials.report_admin_table} WHERE start = end"
        if user:
            admin_list_query = admin_list_query + f" AND user = '{user}'"
        # print (f"admin_list_query: {admin_list_query}") if MyPrintCondition.fprint else 0
        logger_admin.info (f"admin_list_query: {admin_list_query}")
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor:
            my_cursor.execute(admin_list_query)
            admin_query_results = my_cursor.fetchall()        
        # print (f"admin_query_results: {admin_query_results}") if MyPrintCondition.fprint else 0
        logger_admin.info (f"admin_query_results: {admin_query_results}")
        print (f"{user} is not admin" if len(admin_query_results) == 0 else f"{user} is admin since {admin_query_results[0][1]}") if MyPrintCondition.fprint else 0
        logger_admin.info (f"{user} is not admin" if len(admin_query_results) == 0 else f"{user} is admin since {admin_query_results[0][1]}")
        return admin_query_results
    except my_connection.Error as e:
        print (f"admin record error for user < {user} > in query = {admin_list_query}\n{e}") if MyPrintCondition.fprint else 0
        logger_admin.error (f"admin record error for user < {user} > in query = {admin_list_query}\n{e}")
        
def admin_update(user, mode):
    """
    Updates admin status of specific user by adding or removing the user from admin table.
    """
    try:
        # print(user, mode)
        admins = admin_list(user)
        admin_update_query = ""
        if mode == "activate":
            if len(admins) > 0:                
                print (f"{user} is adlready admin since {admins[0][1]}") if MyPrintCondition.fprint else 0
                logger_admin.info (f"{user} is adlready admin since {admins[0][1]}")
            else:
                admin_update_query = f"INSERT INTO {MyCredentials.report_admin_table} (user, start, end) VALUES ('{user}', '{MyBrackets.local_time}', '{MyBrackets.local_time}')"
        elif mode == "deactivate":
            if len(admins) == 0:
                print (f"{user} is not admin already") if MyPrintCondition.fprint else 0
                logger_admin.info (f"{user} is not admin already")
            else:
                admin_update_query = f"UPDATE {MyCredentials.report_admin_table} SET end = '{MyBrackets.local_time}' WHERE user = '{user}' AND start = end"
        if admin_update_query:
            my_connection.ping()  # reconnecting mysql in case of connection timed out
            with my_connection.cursor() as my_cursor:
                my_cursor.execute(admin_update_query)
                my_connection.commit()
            # print (f"admin_update_query: {admin_update_query}") if MyPrintCondition.fprint else 0 
            logger_admin.info (f"admin_update_query: {admin_update_query}")
            print (f"{my_cursor.rowcount} record(s) inserted/updated in admin table") if MyPrintCondition.fprint else 0 
            logger_admin.info (f"{my_cursor.rowcount} record(s) inserted/updated in admin table")
            admin_list(user)
       
    except my_connection.Error as e:
        print (f"admin record error for user < {user} > in query = {admin_update_query}\n{e}") if MyPrintCondition.fprint else 0
        logger_admin.error (f"admin record error for user < {user} > in query = {admin_update_query}\n{e}")