# inserts new record as user group in guacamole makeing connection link in user's guacamole dashboard
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.lib.database import Database as MyDatabase
my_connection = MyDatabase.connect_guaca_db()

pool_records = Capture_log("booking/pool", __file__)
logger_unix = pool_records.log_agent("linux")   # windows logger is needed by passing the node

def insert(x,y):
    try:
        allocation = f"INSERT INTO guacamole_user_group_member (member_entity_id, user_group_id) VALUES ('{x}','{y}')"  # WHERE member_entity_id
        my_connection.ping()  # reconnecting mysql in case of connection timed out
        with my_connection.cursor() as cursor:
            cursor.execute(allocation)
            my_connection.commit()
        print (f"{cursor.rowcount} record(s) inserted") if MyPrintCondition.fprint else 0  
        logger_unix.info (f"{cursor.rowcount} record(s) inserted")  
        
    except:
        print (f"error inserting record for user member entity id < {x} > in group id < {y} >") if MyPrintCondition.fprint else 0
        logger_unix.error (f"error inserting record for user member entity id < {x} > in group id < {y} >")