# updates user group records in guacamole making changes to connection links in user's guacamole dashboard
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_guaca_db()

pool_records = Capture_log("booking/pool", __file__)
logger_unix = pool_records.log_agent("linux")   # windows logger is needed by passing the node

def update (x,y):
    try:
        print (f"x(member_entity_id): {x}, y(user_group_id): {y}") if MyPrintCondition.fprint else 0
        logger_unix.info (f"x(member_entity_id): {x}, y(user_group_id): {y}")
        # allocation = "UPDATE guacamole_user_group_member SET member_entity_id = '%s' WHERE user_group_id = '%s'" %(x, y)  # when simeltanous multiple booking not allowed
        allocation = f"UPDATE guacamole_user_group_member SET user_group_id = '{y}' WHERE member_entity_id = '{x}'"             # when simeltanous multiple booking allowed
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(allocation)
            my_connection.commit()
        print (f"{cursor.rowcount} record(s) affected by updating allocation") if MyPrintCondition.fprint else 0
        logger_unix.info (f"{cursor.rowcount} record(s) affected by updating allocation")
        
    except:
        print (f"error updating the record for member_entity_id < {x} > and user_group_id < {y} >") if MyPrintCondition.fprint else 0
        logger_unix.error (f"error updating the record for member_entity_id < {x} > and user_group_id < {y} >")