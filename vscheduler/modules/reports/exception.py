# called by stat tool
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.lib.database import Database as MyDatabase
from vscheduler.general.timer import Brackets as MyBrackets

my_connection = MyDatabase.connect_report_db()

records = Capture_log("exception", __file__)
logger_exception = records.log_agent("exception")


def exception_list(user, start, end):
    """
    Lists excepted users or 
    queries exception status for specific user.
    """
    try:
        exception_list_query = f"SELECT user, start, end, wall_time FROM {MyCredentials.report_exception_table} WHERE start = end"
        if user:
            exception_list_query = exception_list_query + f" AND user = '{user}'"
        if start:
            exception_list_query = exception_list_query + f" AND start >= '{start}'"
        if end:
            exception_list_query = exception_list_query + f" AND end <= '{end}'"
        # print (f"exception_list_query: {exception_list_query}") if MyPrintCondition.fprint else 0
        logger_exception.info (f"exception_list_query: {exception_list_query}")
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as my_cursor:
            my_cursor.execute(exception_list_query)
            exception_query_results = my_cursor.fetchall()        
        # print (f"exception_query_results: {exception_query_results}") if MyPrintCondition.fprint else 0
        logger_exception.info (f"exception_query_results: {exception_query_results}")
        print (f"{user} is not excepted" if len(exception_query_results) == 0 else f"{exception_query_results[0][0]} is excepted since {exception_query_results[0][1]} with wall time of {exception_query_results[0][3]} hours") if MyPrintCondition.fprint else 0
        logger_exception.info (f"{user} is not exception" if len(exception_query_results) == 0 else f"{exception_query_results[0][0]} is excepted since {exception_query_results[0][1]} with wall time of {exception_query_results[0][3]} hours")
        return exception_query_results
    except my_connection.Error as e:
        print (f"exception record error for user < {user} > in query = {exception_list_query}\n{e}") if MyPrintCondition.fprint else 0
        logger_exception.error (f"exception record error for user < {user} > in query = {exception_list_query}\n{e}")
        
def exception_update(user, mode, wall_time):
    """
    Updates exception status of specific user by adding or removing the user from exception table.
    """
    try:
        # print(user, mode)
        exceptions = exception_list(user, "", "")
        exception_update_query = ""
        if mode == "activate":
            if len(exceptions) > 0:                
                print (f"{user} is already excepted since {exceptions[0][1]} with wall time of {exceptions[0][3]} hours") if MyPrintCondition.fprint else 0
                logger_exception.info (f"{user} is already excepted since {exceptions[0][1]} with wall time of {exceptions[0][3]} hours")
            else:
                exception_update_query = f"INSERT INTO {MyCredentials.report_exception_table} (user, start, end, wall_time) VALUES ('{user}', '{MyBrackets.local_time}', '{MyBrackets.local_time}', {wall_time})"
        elif mode == "deactivate":
            if len(exceptions) == 0:
                print (f"{user} is not excepted already") if MyPrintCondition.fprint else 0
                logger_exception.info (f"{user} is not excepted already")
            else:
                exception_update_query = f"UPDATE {MyCredentials.report_exception_table} SET end = '{MyBrackets.local_time}' WHERE user = '{user}' AND start = end"
        if exception_update_query:
            my_connection.ping()  # reconnecting mysql in case of connection timed out
            with my_connection.cursor() as my_cursor:
                my_cursor.execute(exception_update_query)
                my_connection.commit()
            # print (f"exception_update_query: {exception_update_query}") if MyPrintCondition.fprint else 0 
            logger_exception.info (f"exception_update_query: {exception_update_query}")
            print (f"{my_cursor.rowcount} record(s) inserted/updated into exception table") if MyPrintCondition.fprint else 0 
            logger_exception.info (f"{my_cursor.rowcount} record(s) inserted/updated into exception table")
            exception_list(user, "", "")
       
    except my_connection.Error as e:
        print (f"exception record error for user < {user} > in query = {exception_update_query}\n{e}") if MyPrintCondition.fprint else 0
        logger_exception.error (f"exception record error for user < {user} > in query = {exception_update_query}\n{e}")