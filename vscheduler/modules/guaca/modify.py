# removes user group record from guacamole deleting connection link from user's guacamole dashboard
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_guaca_db()
my_cursor = my_connection.cursor()

pool_records = Capture_log("pool", __file__)
logger = pool_records.log_agent()

def modify(x,y):
    try:
        if x:
            reset = "DELETE FROM guacamole_user_group_member WHERE member_entity_id = '%s' AND user_group_id = '%s'" %(x, y)
        else:
            reset = "DELETE FROM guacamole_user_group_member WHERE user_group_id = '%s'" %(y)
        my_cursor.execute(reset)
        my_connection.commit()
        print (f"{my_cursor.rowcount} record(s) affected") if MyPrintCondition.fprint else 0
        logger.info (f"{my_cursor.rowcount} record(s) affected")
        if my_cursor.rowcount:
            print("session link was removed for member entiry id <", x,"> in user group id <", y,">") if MyPrintCondition.fprint and x else 0
            print("session link was removed for user group id <", y,">") if MyPrintCondition.fprint and not x else 0
            logger.info ("session link was removed for member entiry id < {x} > in user group id < {y} >") if x else 0
            logger.info ("session link was removed for user group id < {y} >") if not x else 0
    except:
        print (f"error deleting recorde for member_entity_id < {x} > and user_group_id < {y} >") if MyPrintCondition.fprint else 0
        logger.error (f"error deleting recorde for member_entity_id < {x} > and user_group_id < {y} >")