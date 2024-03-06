# updates user group records in guacamole making changes to connection links in user's guacamole dashboard
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_guaca_db()
from vscheduler.modules.guaca.entity import entity
from vscheduler.modules.guaca.guaca_user_group import guacamole_user_group

pool_records = Capture_log("booking/pool", __file__)
logger_unix = pool_records.log_agent("linux")   # windows logger is needed by passing the node

def update (x,y,z, caller):
    try:
        print (f"x(member_entity_id): {x}, y(user_group_id): {y}") if MyPrintCondition.fprint else 0
        logger_unix.info (f"x(member_entity_id): {x}, y(user_group_id): {y}, z(pool_group_id): {z}")
        windows_pool_entity = entity(MyCredentials.windows_pool)
        linux_pool_entity = entity(MyCredentials.linux_pool)
        windows_pool_user_group = guacamole_user_group(windows_pool_entity[0][0])
        linux_pool_user_group = guacamole_user_group(linux_pool_entity[0][0])
        # allocation = "UPDATE guacamole_user_group_member SET member_entity_id = '%s' WHERE user_group_id = '%s'" %(x, y)  # when simeltanous multiple booking not allowed
        if caller == "alloc":
            allocation = f"UPDATE guacamole_user_group_member SET user_group_id = '{y}' WHERE member_entity_id = '{x}' AND (user_group_id = '{windows_pool_user_group[0][0]}' OR user_group_id = '{linux_pool_user_group[0][0]}')"
        elif caller == "revert" or caller == "sync":
            allocation = f"UPDATE guacamole_user_group_member SET user_group_id = '{y}' WHERE member_entity_id = '{x}' AND user_group_id != '{windows_pool_user_group[0][0]}' AND user_group_id != '{linux_pool_user_group[0][0]}'"
            # allocation = f"UPDATE guacamole_user_group_member SET user_group_id = '{y}' WHERE member_entity_id = '{x}' AND user_group_id != '{z}'" if z else f"UPDATE guacamole_user_group_member SET user_group_id = '{y}' WHERE member_entity_id = '{x}'"             # when simeltanous multiple booking allowed
        logger_unix.info (f"allocation= {allocation}")
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(allocation)
            my_connection.commit()
            print (f"{cursor.rowcount} record(s) affected by updating allocation") if MyPrintCondition.fprint else 0
            logger_unix.info (f"{cursor.rowcount} record(s) affected by updating allocation")
        
    except my_connection.Error as e:
        print (f"error updating the record for member_entity_id < {x} > and user_group_id < {y} >\n{e}") if MyPrintCondition.fprint else 0
        logger_unix.error (f"error updating the record for member_entity_id < {x} > and user_group_id < {y} >\n{e}")