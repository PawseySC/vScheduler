from vscheduler.log.log import CaptureLog
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.verbose import verbose
from vscheduler.lib.database import Database as MyDatabase

my_connection = MyDatabase.connect_guaca_db()

modify_records = CaptureLog("modify", __file__)
logger = modify_records.log_agent("guaca")


def modify(x,y):
    """
    Removes user group record from guacamole deleting connection link from user's guacamole dashboard
    """
    try:
        if x:
            reset = f"DELETE FROM guacamole_user_group_member WHERE member_entity_id = '{x}' AND user_group_id = '{y}'"
        else:
            reset = f"DELETE FROM guacamole_user_group_member WHERE user_group_id = '{y}'"
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(reset)
            my_connection.commit()
        print (f"{cursor.rowcount} record(s) affected") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.info (f"{cursor.rowcount} record(s) affected")
        if cursor.rowcount:
            print(f"session link was removed for member entiry id < {x} > in user group id < {y} >") if verbose.mode else 0 # if MyPrintCondition.fprint and x else 0
            print(f"session link was removed for user group id < {y} >") if verbose.mode and not x else 0 # if MyPrintCondition.fprint and not x else 0
            logger.info (f"session link was removed for member entiry id < {x} > in user group id < {y} >") if x else 0
            logger.info (f"session link was removed for user group id < {y} >") if not x else 0
        
    except:
        print (f"error deleting recorde for member_entity_id < {x} > and user_group_id < {y} >") if verbose.mode else 0 # if MyPrintCondition.fprint else 0
        logger.error (f"error deleting recorde for member_entity_id < {x} > and user_group_id < {y} >")