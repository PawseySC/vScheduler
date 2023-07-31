# updates user group records in guacamole making changes to connection links in user's guacamole dashboard
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_guaca_db()
my_cursor = my_connection.cursor()

pool_records = Capture_log("pool", __file__)
logger = pool_records.log_agent()

def update (x,y):
    try:
        print (f"x(member_entity_id): {x}, y(user_group_id): {y}") if MyPrintCondition.fprint else 0
        logger.info (f"x(member_entity_id): {x}, y(user_group_id): {y}")
        # allocation = "UPDATE guacamole_user_group_member SET member_entity_id = '%s' WHERE user_group_id = '%s'" %(x, y)  # when simeltanous multiple booking not allowed
        allocation = "UPDATE guacamole_user_group_member SET user_group_id = '%s' WHERE member_entity_id = '%s'" %(y, x)  # when simeltanous multiple booking allowed
        my_cursor.execute(allocation)
        my_connection.commit()
        print (f"{my_cursor.rowcount} record(s) affected by updating allocation") if MyPrintCondition.fprint else 0
        logger.info (f"{my_cursor.rowcount} record(s) affected by updating allocation")
    except:
        print (f"error updating the record for member_entity_id < {x} > and user_group_id < {y} >") if MyPrintCondition.fprint else 0
        logger.error (f"error updating the record for member_entity_id < {x} > and user_group_id < {y} >")